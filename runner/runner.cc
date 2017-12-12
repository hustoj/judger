#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/syscall.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fstream>
#include <vector>
#include <sys/resource.h>
#include <sys/user.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <sys/ptrace.h>
#include <string.h>
#include <errno.h>
#include <syslog.h>
#include "result.h"

#ifdef __i386
#define REG_SYSCALL orig_eax
#else
#define REG_SYSCALL orig_rax
#endif

#define STD_MB 1048576
#define STD_T_LIM 2
#define STD_FILE_LIMIT (STD_MB << 3)
#define STD_MEMORY_LIMIT (STD_MB << 7)
#define bufsize 512

#define DEBUG 0
#define NEXT_CONTINUE 0
#define NEXT_STOP 1
#define NEXT_NORMAL 2

#define USER_ID 1536
#define BUFFER_SIZE 1024

int syscall_counter[512];

//c & c++
int LANG_CV[256] = {85, 8, 140, SYS_time, SYS_read, SYS_uname, SYS_write, SYS_open,
                    SYS_close, SYS_execve, SYS_access, SYS_brk, SYS_munmap, SYS_mprotect,
                    SYS_mmap, SYS_fstat, SYS_set_thread_area, 252, 0};

using namespace std;

class Setting
{
  public:
    string commandName;
    string working_dir;
    vector<string> args;
    int time_limit;
    int running_user_id;
    int memory_limit;
};

class Result
{
  public:
    string result;
    int retcode;
    int used_time;
    int used_memory;
};

Setting setting;
Result result;

int load_config();
int set_resource_limit();
int reset_io();
int write_result();
int monitor_child(pid_t pid);
int calc_child_spend_time(struct rusage *rusage);
int check_memory(pid_t pid);
int detect_signal(int sig);
int check_status(int status, pid_t pid);
int initial();
int run();
int initial_syscall_limits();
int get_proc_info(pid_t pid, string field);

int main()
{
    initial();

    run();

    return 0;
}

int do_change_root()
{
    // current user should be root, so can change root path
    int ret = chroot(setting.working_dir.c_str());
    if (ret != 0)
    {
        syslog(LOG_ERR, "chroot failed");
        exit(5);
    }

    return 0;
}

int run()
{
    pid_t child_pid = fork();
    
    do_change_root();

    if (child_pid == 0)
    {
        // child
        set_resource_limit();

        int ret;
        ret = setuid(setting.running_user_id);

        reset_io();

        string name = "./Main";

        ptrace(PTRACE_TRACEME, 0, NULL, NULL);
        ret = execl(name.c_str(), name.c_str(), NULL);
        if (ret == -1)
        {
            syslog(LOG_ERR, "excel failed!");
        }

        return 0;
    }
    else
    {
        syslog(LOG_INFO, "monitor %d", child_pid);
        // parent
        monitor_child(child_pid);
        write_result();
        return 0;
    }
}

int monitor_child(pid_t pid)
{
    int status;
    struct user_regs_struct reg;
    struct rusage ruse;
    int current_duration;
    while (true)
    {
        wait4(pid, &status, 0, &ruse);

        int ret = check_status(status, pid);

        if (ret == NEXT_STOP)
        {
            break;
        }

        check_memory(pid);

        if (ret == NEXT_CONTINUE)
        {
            continue;
        }
        // detect regs
    }
    calc_child_spend_time(&ruse);
}

int initial()
{
    load_config();

    openlog("runner", LOG_PERROR | LOG_CONS, LOG_USER);
    syslog(LOG_INFO, "woring in %s", setting.working_dir.c_str());

    result.retcode = OJ_AC;
    result.used_memory = 0;
    result.used_time = 0;

    initial_syscall_limits();
}

int initial_syscall_limits()
{
    // memset(syscall_counter, 0, sizeof(syscall_counter));
    // for (int i = 0; LANG_CV[i]; i++)
    // {
    //     syscall_counter[LANG_CV[i]] = LANG_CC[i];
    // }
    return 0;
}

int check_status(int status, pid_t pid)
{
    int sig;
    // general stopped
    if (WIFEXITED(status))
    {
        result.retcode = OJ_AC;
        return NEXT_STOP;
    }

    // child exit by signal
    if (WIFSIGNALED(status))
    {
        sig = WTERMSIG(status);
        detect_signal(sig);
        return NEXT_STOP;
    }

    // child suspend, detect stop signal
    if (WIFSTOPPED(status))
    {
        sig = WSTOPSIG(status);

        if (sig == SIGTRAP)
        {
            ptrace(PTRACE_SYSCALL, pid, NULL, NULL);
            return NEXT_CONTINUE;
        }
        detect_signal(sig);
        // should not recieve other signal but SIGTRAP
        // so kill app
        ptrace(PTRACE_KILL, pid, NULL, NULL);
        return NEXT_STOP;
    }

    return NEXT_NORMAL;
}

int detect_signal(int sig)
{
    if (result.retcode != OJ_AC)
    {
        return 0;
    }
    switch (sig)
    {
    case SIGALRM:
    case SIGXCPU:
        result.retcode = OJ_TL;
        break;
    case SIGXFSZ:
        result.retcode = OJ_OL;
        break;
    default:
        result.retcode = OJ_RE;
    }
    return 0;
}

int check_memory(int pid)
{
    // VmHWM and VmRSS are the process’s peak/current usage of physical RAM.
    int current_memory = get_proc_info(pid, "VmHWM");

    if (current_memory > result.used_memory)
    {
        result.used_memory = current_memory;
    }

    // detect if current memory large then limit
    if (result.used_memory > 10 * 1024 * 1024)
    {
        if (result.retcode == OJ_AC)
        {
            result.retcode = OJ_ML;
        }
        ptrace(PTRACE_KILL, pid, NULL, NULL);
    }
    return 0;
}

int get_proc_info(pid_t pid, string field)
{
    char fpath[BUFFER_SIZE], line_buff[BUFFER_SIZE], ignore[BUFFER_SIZE];
    sprintf(fpath, "/proc/%d/status", pid);

    ifstream inf(fpath);
    if (!inf)
    {
        return 0;
    }
    int field_len = field.length();
    int value;
    while (!inf.eof())
    {
        inf.getline(line_buff, 200);
        if (strncmp(line_buff, field.c_str(), field_len) == 0)
        {
            sscanf(line_buff, "%s %d", ignore, &value);
            return value;
        }
    }
    syslog(LOG_ERR, "not found %s", field.c_str());
    return 0;
}

int load_config()
{
    char buff[BUFFER_SIZE];
    getcwd(buff, BUFFER_SIZE - 1);
    setting.working_dir = buff;

    ifstream configFile("case.conf");
    // configFile >> setting.working_dir;
    // configFile >> setting.running_user_id;
    setting.running_user_id = 1001;

    configFile >> setting.time_limit;
    configFile >> setting.memory_limit;

    return 0;
}

int reset_io()
{
    FILE *fd = freopen("data.in", "r", stdin);
    if (fd == NULL)
    {
        syslog(LOG_ERR, "stdin failed");
    }

    int file_mode = S_IWOTH | S_IWUSR | S_IRUSR | S_IROTH;

    fd = freopen("user.out", "w", stdout);
    if (fd == NULL)
    {
        syslog(LOG_ERR, "stdout failed");
    }

    chmod("user.out", file_mode);

    fd = freopen("user.error", "w", stderr);
    if (fd == NULL)
    {
        syslog(LOG_ERR, "stderror failed");
    }
    chmod("user.error", file_mode);

    return 0;
}

int calc_child_spend_time(struct rusage *usage)
{
    // use time
    result.used_time += (usage->ru_utime.tv_sec * 1000 + usage->ru_utime.tv_usec / 1000);
    // sys time
    result.used_time += (usage->ru_stime.tv_sec * 1000 + usage->ru_stime.tv_usec / 1000);

    return 0;
}

int write_result()
{
    ofstream resultFile("result.txt");

    if (!resultFile.is_open())
    {
        syslog(LOG_ERR, "open result file failed\n");
    }
    resultFile << result.retcode << endl;
    resultFile << result.used_time << endl;
    resultFile << result.used_memory << endl;
    resultFile.close();
    return 0;
}

int set_resource_limit()
{
    // set the limit
    struct rlimit rlim; // time limit, file limit& memory limit

    // time limit
    int time_left = setting.time_limit;
    rlim.rlim_max = time_left + 1;
    rlim.rlim_cur = time_left;
    setrlimit(RLIMIT_CPU, &rlim);

    // alarm, set max running time
    alarm(rlim.rlim_cur * 2 + 3);

    // file limit
    rlim.rlim_max = STD_FILE_LIMIT + STD_MB * 8;
    rlim.rlim_cur = STD_FILE_LIMIT + STD_MB * 8;
    setrlimit(RLIMIT_FSIZE, &rlim);

    // proc limit
    rlim.rlim_cur = 20;
    rlim.rlim_max = 20;
    setrlimit(RLIMIT_NPROC, &rlim);
    // set the stack
    rlim.rlim_cur = STD_MB << 3;
    rlim.rlim_max = STD_MB << 3;
    setrlimit(RLIMIT_STACK, &rlim);

    return 0;
}