package main

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
)

const (
	sizeLimitMB = 50
	sizeLimitBytes = sizeLimitMB * 1024 * 1024
)

type FileInfo struct {
	Path string
	Size int64
}

func parseGitignore(gitignorePath string) ([]string, error) {
	file, err := os.Open(gitignorePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var patterns []string
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line != "" && !strings.HasPrefix(line, "#") {
			patterns = append(patterns, line)
		}
	}
	return patterns, scanner.Err()
}

func isIgnored(path string, ignorePatterns []string) bool {
	for _, pattern := range ignorePatterns {
		matched, err := filepath.Match(pattern, filepath.Base(path))
		if err == nil && matched {
			return true
		}
		matched, err = filepath.Match(pattern, path)
		if err == nil && matched {
			return true
		}
	}
	return false
}

func findLargeFiles(dir string, ignorePatterns []string) []FileInfo {
	var largeFiles []FileInfo
	var mutex sync.Mutex
	var wg sync.WaitGroup

	filepath.Walk(dir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}

		if info.IsDir() {
			if isIgnored(path, ignorePatterns) {
				return filepath.SkipDir
			}
			return nil
		}

		if !isIgnored(path, ignorePatterns) && info.Size() > sizeLimitBytes {
			wg.Add(1)
			go func() {
				defer wg.Done()
				mutex.Lock()
				largeFiles = append(largeFiles, FileInfo{Path: path, Size: info.Size()})
				mutex.Unlock()
			}()
		}

		return nil
	})

	wg.Wait()
	return largeFiles
}

func main() {
	var dir string
	if len(os.Args) > 1 {
		dir = os.Args[1]
	} else {
		var err error
		dir, err = os.Getwd()
		if err != nil {
			fmt.Println("Error getting current directory:", err)
			return
		}
	}

	gitignorePath := filepath.Join(dir, ".gitignore")
	ignorePatterns, err := parseGitignore(gitignorePath)
	if err != nil {
		fmt.Println("Warning: Could not parse .gitignore:", err)
	}

	fmt.Printf("Searching for files larger than %d MiB in: %s\n", sizeLimitMB, dir)
	fmt.Println("(Respecting .gitignore rules)")

	largeFiles := findLargeFiles(dir, ignorePatterns)

	if len(largeFiles) > 0 {
		fmt.Println("\nLarge files found:")
		sort.Slice(largeFiles, func(i, j int) bool {
			return largeFiles[i].Size > largeFiles[j].Size
		})
		for _, file := range largeFiles {
			fmt.Printf("%s: %.2f MiB\n", file.Path, float64(file.Size)/(1024*1024))
		}
	} else {
		fmt.Printf("\nNo files larger than %d MiB found.\n", sizeLimitMB)
	}

	fmt.Printf("\nTotal number of large files: %d\n", len(largeFiles))
}