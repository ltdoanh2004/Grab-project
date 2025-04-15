package logger

import (
	"os"

	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
)

func Init() {
	logger := zerolog.New(os.Stdout).
		With().
		Timestamp().
		Logger().Output(zerolog.ConsoleWriter{Out: os.Stdout})
	log.Logger = logger

	// Set global log level
	zerolog.SetGlobalLevel(zerolog.DebugLevel)
}
