package main

import (
	"encoding/json"
	"fmt"
)

func main() {
	result := make(map[string]interface{})
	result["memory"] = 200
	result["time"] = 7
	result["status"] = 4

	str, err := json.Marshal(result)
	if err != nil {
		panic("json failed!")
	}
	fmt.Println(string(str))
}
