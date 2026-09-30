package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/fsnotify/fsnotify"
)

const watchedFile = "/etc/ssh/sshd_config"

type Event struct {
	Event     string `json:"event"`
	Path      string `json:"path"`
	Timestamp string `json:"timestamp"`
}

func main() {
	watcher, err := fsnotify.NewWatcher()
	if err != nil {
		log.Fatal(err)
	}
	defer watcher.Close()

	if err := watcher.Add(watchedFile); err != nil {
		log.Fatal(err)
	}

	for {
		select {
		case event, ok := <-watcher.Events:
			if !ok {
				return
			}

			if event.Name == watchedFile && event.Op&fsnotify.Write == fsnotify.Write {
				output := Event{
					Event:     "MODIFY",
					Path:      event.Name,
					Timestamp: time.Now().UTC().Format(time.RFC3339),
				}

				data, err := json.Marshal(output)
				if err != nil {
					log.Println("JSON error:", err)
					continue
				}

				fmt.Println(string(data))
			}

		case err, ok := <-watcher.Errors:
			if !ok {
				return
			}

			log.Println("Watcher error:", err)
		}
	}
}
