package main

import (
	"encoding/json"
	"fmt"
)

func main() {
	result := make(map[string]interface{})
	result["memory_cost"] = 200
	result["time_cost"] = 7
	result["result"] = 4

	str, err := json.Marshal(result)
	if err != nil {
		panic("json failed!")
	}
	fmt.Println(string(str))
}
