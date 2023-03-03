package main

import (
	"fmt"
	"io"
	"os/exec"
)

type ModelNotRunningError struct{}

func (e ModelNotRunningError) Error() string {
	return "The model is not currently running. Use Model.Start() first."
}

// Our model type that will hold the model process and handle querying it
type Model struct {
	process *exec.Cmd
	stdin   io.WriteCloser
	stdout  io.ReadCloser

	isRunning bool
}

func NewModel(files []string) *Model {
	// Define our command to be run along with its args
	// Here the command is our venv's python, and the args include the python
	// program we want to run (i.e. search.py)
	py := exec.Command("./venv/bin/python", "search.py", "--interactive")
	// append our arguments onto the end of the command
	// NOTE: trying to do this during the cmd init will break the python code
	// TODO add flags/options to the args
	py.Args = append(py.Args, files...)

	m := Model{
		process:   py,
		isRunning: false,
	}

	return &m
}

// Start the model's process
func (m Model) Start() error {
	err := m.process.Run()
	m.isRunning = true
	return err
}

// Close the model's process
func (m Model) Close() {
	m.stdin.Write([]byte("quit"))
	m.isRunning = false
}

func (m Model) Query(queries []string) (string, error) {
	if !m.isRunning {
		return "", ModelNotRunningError{}
	}

	// Build our string of queries
	query := ""
	for _, q := range queries {
		query += fmt.Sprintf("%s", q)
	}
	query += "\n"

	// Write our query to the model
	m.stdin.Write([]byte(query))

	// Consume the output of the model as a byte slice
	var result []byte
	_, err := m.stdout.Read(result)
	if err != nil {
		return "", err
	}

	return string(result), nil
}
