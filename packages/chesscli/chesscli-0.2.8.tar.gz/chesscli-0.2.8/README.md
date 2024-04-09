# ChessCLI

ChessCLI is a command-line interface (CLI) tool designed to streamline the development environment for a chess game project. It automates tasks such as setting up the project, opening the codebase in Visual Studio Code, and managing Docker containers.

## Features

- **Easy Configuration**: Quickly configure the path to your chess game project repository.
- **Code Access**: Open your chess game project in Visual Studio Code with a single command.
- **Docker Management**: Start and stop your Docker containers directly through the CLI, simplifying your workflow.

## Installation

To install ChessCLI, run the following command in your terminal:

```bash
pip install chesscli
```

## Usage

Here are some of the commands you can use with ChessCLI:

- **Setup**: If you haven't cloned the chess game repository yet, this command helps you clone it and set up your development environment.

  ```bash
  chesscli setup
  ```

- **Configure**: Configure the path to your existing chess game project repository.

  ```bash
  chesscli configure
  ```

- **Open in VS Code**: Open the configured chess game project in Visual Studio Code.

  ```bash
  chesscli code
  ```

- **Start Docker Containers**: Start the Docker containers needed for your project.

  ```bash
  chesscli start
  ```

- **Stop Docker Containers**: Stop the Docker containers.

  ```bash
  chesscli stop
  ```

## Development

Want to contribute? Great! ChessCLI is open for contributions. Whether it's fixing bugs, adding new features, or improving the documentation, all contributions are welcome.

## License

ChessCLI is released under the [MIT License](LICENSE). See the LICENSE file for more details.

## Acknowledgments

- Thanks to all the contributors who spend time to improve ChessCLI.
- Special thanks to [Typer](https://typer.tiangolo.com/), which made creating this CLI tool a breeze.
