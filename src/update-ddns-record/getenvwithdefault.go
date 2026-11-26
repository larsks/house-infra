package main

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

// GetenvWithDefault is a typed version of os.Getenv that allows you to
// specify a default value. The return type of the method is the type
// of the defaultValue argument. Currently supported types:
//
//   - string
//   - int
//   - bool
//   - float64
//   - time.Duration
//   - time.Time (must provide format as third argument)
//
// If you use any other type you will always get the default value.
func GetenvWithDefault[T any](name string, defaultValue T, options ...any) (value T) {
	val := os.Getenv(name)
	if val == "" {
		return defaultValue
	}

	var result any
	var zero T

	switch any(zero).(type) {
	case string:
		result = val
	case int:
		v, err := strconv.Atoi(val)
		if err != nil {
			return defaultValue
		}
		result = v
	case bool:
		v, err := strconv.ParseBool(val)
		if err != nil {
			return defaultValue
		}
		result = v
	case float64:
		v, err := strconv.ParseFloat(val, 64)
		if err != nil {
			return defaultValue
		}
		result = v
	case time.Duration:
		v, err := time.ParseDuration(val)
		if err != nil {
			return defaultValue
		}
		result = v
	case time.Time:
		if len(options) == 0 {
			return defaultValue
		}
		v, err := tryParseTime(val, options)
		if err != nil {
			return defaultValue
		}
		result = v
	default:
		return defaultValue
	}

	return result.(T)
}

func tryParseTime(val string, formats []any) (time.Time, error) {
	for _, format := range formats {
		switch format := format.(type) {
		case string:
			if res, err := time.Parse(format, val); err == nil {
				return res, nil
			}
		}
	}

	return time.Time{}, fmt.Errorf("invalid time format")
}
