/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"os"

	"github.com/spf13/cobra"
)

// TODO abstract this into a module that handles querying and results

// Represents a result with a file name and it's similary score to our query
type item struct {
	name  string
	score float32
}

// Handles sorting of items by their score
type sortByScore []item

func (a sortByScore) Len() int           { return len(a) }
func (a sortByScore) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }
func (a sortByScore) Less(i, j int) bool { return a[i].score < a[j].score }

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "fim",
	Short: "A brief description of your application",
	Long: `A longer description that spans multiple lines and likely contains
examples and usage of using your application. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	// Uncomment the following line if your bare application
	// has an action associated with it:
	// Run: func(cmd *cobra.Command, args []string) {
	// fmt.Println("Root Called")
	// },
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func init() {
	// Here you will define your flags and configuration settings.
	// Cobra supports persistent flags, which, if defined here,
	// will be global for your application.

	// rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.search.yaml)")

	// Cobra also supports local flags, which will only run
	// when this action is called directly.

}
