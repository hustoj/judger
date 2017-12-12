all:
	g++ -o runner runner.cc 

test:
	gcc -o Main test.cc --static -ansi -fno-asm -O2 -Wall -lm

clean:
	rm runner Main user.* result.txt
