# LangTrace - Trace Attributes

This repository hosts the JSON schema definitions and the generated model code for both Python and TypeScript. It's designed to streamline the development process across different programming languages, ensuring consistency in data structure and validation logic. The repository includes tools for automatically generating model code from JSON schema definitions, simplifying the task of keeping model implementations synchronized with schema changes.

## Repository Structure

```
/
├── schemas/                      # JSON schema definitions
│   └── openai_span_attributes.json
├── scripts/                      # Shell scripts for model generation
│   └── generate_python.sh
├── generated/                    # Generated model code
│   ├── python/                   # Python models
│   └── typescript/               # TypeScript interfaces
├── package.json
├── requirements.txt
├── README.md
└── .gitignore
```

## Prerequisites

Before you begin, make sure you have the following installed on your system:

- Node.js and npm
- Python and pip
- `ts-node` for running TypeScript scripts directly (install globally via `npm install -g ts-node`)
- `datamodel-code-generator` for Python model generation (install via `pip install datamodel-code-generator`)

## Generating Models

### Python Models

To generate Python models from a JSON schema, use the `generate_python.sh` script located in the `scripts` directory. This script takes the path to a JSON schema file as an argument and generates a Python model in the `generated/python` directory.

```sh
./scripts/generate_python.sh schemas/openai_span_attributes.json
```

### TypeScript Interfaces

To generate TypeScript interfaces from a JSON schema, use the `schema_to_interface.ts` script located in the `src/models` directory. This script also takes the path to a JSON schema file as an argument and generates a TypeScript interface in the `generated/typescript` directory.
t

```sh
ts-node scripts/generate_typescript.ts schemas/langtrace_span_attributes.json
ts-node scripts/generate_typescript.ts schemas/openai_span_attributes.json
```

To include instructions for building and uploading your Python package to PyPI, as well as how to automate this process using GitHub Actions, you can update your `README.md` file with the following sections:

---

## Contributing

Contributions are welcome! If you'd like to add a new schema or improve the existing model generation process, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Make your changes.
4. Test your changes to ensure the generated models are correct.
5. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the [Apache 2.0](LICENSE). See the LICENSE file for more details.
