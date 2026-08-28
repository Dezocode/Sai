package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"io/fs"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
)

const (
	designAuth     = "apps/apple/Packages/SaiKit/Sources/SaiDesignLanguage"
	featureRoot    = "apps/apple/Packages/SaiKit/Sources/SaiFeatures"
	protoRoot      = "prototypes/plugins"
	protoDesignDir = "PrototypeDesign"
	macShell       = "apps/apple/SaiMac/SaiMacApp.swift"
	iosShell       = "apps/apple/SaiIOS/SaiIOSApp.swift"
)

// PATCHED_FILE_MARKER_REMOVE
