/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"os/exec"
	"sort"

	"github.com/spf13/cobra"
)

// searchCmd represents the search command
var searchCmd = &cobra.Command{
	Use:   "search",
	Short: "Queries images in the current directory",
	Long: `Search allows you to search a directory for images that are
	similar to a given query or set of queries. If given a set of queries,
	they should all be related to a single concept you are searching for.
	Each query should be a string contained in quotes.
	`,
	Args: cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		// create a slice of files to be queried
		files := []string{"cat.jpeg", "dog.jpeg"}

		query := args[0]

		// TODO abstract this into a module that handles querying and results
		// init our command
		// we use ./venv/bin/python here to ensure we can use our imported libraries
		search := exec.Command("./venv/bin/python", "search.py", query)

		// append our arguments onto the end of the command
		// NOTE: trying to do this during the cmd init will break the python code
		// TODO add flags/options to the args
		search.Args = append(search.Args, files...)

		// create buffers for the output from the python script
		var out bytes.Buffer
		var stderr bytes.Buffer
		search.Stdout = &out
		search.Stderr = &stderr

		err := search.Run()
		if err != nil {
			fmt.Println(err)
		}

		// unmarshal the data from our script
		// TODO consider building a custom parser to put this data into a list of structs rather than a map
		scores := map[string]float32{}
		if err := json.Unmarshal(out.Bytes(), &scores); err != nil {
			fmt.Println(err)
		}

		// TODO abstract this into a module that handles querying and results
		// turn our map into a list and sort it by their scores
		scoreSlice := []item{}
		for name, score := range scores {
			scoreSlice = append(scoreSlice, item{name, score})
		}
		fmt.Println(scoreSlice)
		sort.Sort(sort.Reverse(sortByScore(scoreSlice)))

		// TODO abstract results printing into a new func/file
		// print the rank, name, and score of each queried file
		topk, err := cmd.Flags().GetInt("topk")
		if err != nil {
			log.Fatalf("Error while getting topk %s", err)
		}

		// get the min between the topk and the # of results
		var limit int
		if topk < len(scoreSlice) {
			limit = topk
		} else {
			limit = len(scoreSlice)
		}
		// print our results line by line
		for i := 0; i < limit; i++ {
			result := scoreSlice[i]
			fmt.Println(i+1, result.name, result.score)
		}
	},
}

func init() {
	rootCmd.AddCommand(searchCmd)
	searchCmd.Flags().IntP("topk", "k", 5, "How many results should be displayed")

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// searchCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// searchCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
