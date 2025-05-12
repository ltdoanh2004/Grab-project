package util

import (
	"bufio"
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"strings"
)

func ReadCSV(filePath string) ([]map[string]string, error) {
	f, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	reader := csv.NewReader(bufio.NewReaderSize(f, 100*1024*1024))
	header, err := reader.Read()
	if err != nil {
		return nil, err
	}

	var records []map[string]string
	line := 0
	for {
		line++
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Fatalf("Error on line %d: %v \n", line, err)
		}
		recordMap := make(map[string]string)
		for i, value := range record {
			// Replace ' by " to avoid JSON parsing issues
			value = strings.ReplaceAll(value, "'", "\"")
			value = strings.ReplaceAll(value, "\\xa0", " ")
			value = strings.TrimSpace(value)
			recordMap[header[i]] = value
			if i == 0 {
				// Remove leading and trailing spaces from the first column
				recordMap["id"] = value
			}
		}
		records = append(records, recordMap)
	}
	fmt.Println("Number of records: ", len(records))
	return records, nil
}
