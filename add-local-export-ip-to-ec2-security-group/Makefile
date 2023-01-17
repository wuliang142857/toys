# note: call scripts from /scripts
CURRENT_PATH				:= $(shell pwd)
APP_NAME					:= add-local-export-ip-to-ec2-security-group
CMD_FILE 					:= $(CURRENT_PATH)/main.go
OUTPUT_DIR					:= $(CURRENT_PATH)/output

.PHONY:all
all: build-darwin-arm64 build-darwin-amd64 build-linux-amd64 build-linux-armv7 build-linux-arm64 build-linux-x86 build-windows-amd64 build-windows-x86

build-darwin-arm64:
	GOOS=darwin GOARCH=arm64 go build -o ${OUTPUT_DIR}/darwin-arm64/${APP_NAME} ${CMD_FILE}

build-darwin-amd64:
	GOOS=darwin GOARCH=amd64 go build -o ${OUTPUT_DIR}/darwin-amd64/${APP_NAME} ${CMD_FILE}

# brew install mingw-w64
build-windows-amd64:
	GOOS=windows GOARCH=amd64 go build -o ${OUTPUT_DIR}/windows-amd64/${APP_NAME} ${CMD_FILE}

build-windows-x86:
	GOOS=windows GOARCH=386 go build -o ${OUTPUT_DIR}/windows-x86/${APP_NAME} ${CMD_FILE}

build-linux-amd64:
	GOOS=linux GOARCH=amd64 go build -o ${OUTPUT_DIR}/linux-amd64/${APP_NAME} ${CMD_FILE}

build-linux-x86:
	GOOS=linux GOARCH=amd64 go build -o ${OUTPUT_DIR}/linux-x86/${APP_NAME} ${CMD_FILE}

build-linux-arm64:
	GOOS=linux GOARCH=amd64 go build -o ${OUTPUT_DIR}/linux-arm64/${APP_NAME} ${CMD_FILE}

build-linux-armv7:
	GOOS=linux GOARCH=arm GOARM=7 go build -o ${OUTPUT_DIR}/linux-armv7/${APP_NAME} ${CMD_FILE}

deps:
	go mod download
	go mod tidy

clean:
	@rm -rf ${OUTPUT_DIR} > /dev/null 2>&1 < /dev/null || echo ""
