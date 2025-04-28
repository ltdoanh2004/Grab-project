package util

import (
	"encoding/csv"
	"os"
	"strings"
)

func ReadCSV(filePath string) ([]map[string]string, error) {
	f, err := os.Open(filePath)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	reader := csv.NewReader(f)
	header, err := reader.Read()
	if err != nil {
		return nil, err
	}

	var records []map[string]string
	for {
		record, err := reader.Read()
		if err != nil {
			break
		}
		recordMap := make(map[string]string)
		for i, value := range record {
			// Replace ' by " to avoid JSON parsing issues
			value = strings.ReplaceAll(value, "'", "\"")
			value = strings.ReplaceAll(value, "\\xa0", " ")
			recordMap[header[i]] = value
		}
		records = append(records, recordMap)
	}

	return records, nil
}
