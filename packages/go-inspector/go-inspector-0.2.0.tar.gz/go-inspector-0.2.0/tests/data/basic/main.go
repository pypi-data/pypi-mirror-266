package main

import (
  "fmt"
  "path/filepath"
)

func main() {
  s := filepath.Join("a", "b", "c")
  fmt.Println(s)
}
