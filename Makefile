all: build clean

build:
	pyinstaller --onefile --name connect4 ./src/play.py

clean:
	rm -r build connect4.spec

