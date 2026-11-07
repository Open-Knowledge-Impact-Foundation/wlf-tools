# Contributing

Contributions to ListGen, campwiz, translations, and documentation are welcome.

## Report a bug or suggest a feature

Open an issue describing the problem or proposed improvement. For bugs, include reproduction steps, expected and actual behavior, and relevant environment details. Include screenshots for interface problems and remove credentials and personal information from logs.

Discuss substantial changes in an issue before starting implementation so maintainers can help clarify scope.

### Add screenshots to issues
![Adding Images to Issues](https://github.com/nokibsarkar/bot-wikifolklore/assets/39087050/93f185c6-c329-43dd-a32c-a585e166ca82)

## Set up a development environment

Fork the repository, clone your fork, and create a branch for your change.

The backend uses Python and FastAPI. From the repository root, create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

The application requires a local `.env` file and configured external services. Review environment variable usage in the backend and arrange development credentials with the maintainers. Keep credentials out of version control and use development services for testing.

The React frontend and Tailwind landing page use Yarn. Their package files specify Yarn 1.22.22. Install dependencies in each directory you need to work on:

```bash
cd frontend
yarn install --frozen-lockfile
yarn start
```

For landing page styling, run these commands from the repository root:

```bash
cd landing_page
yarn install --frozen-lockfile
yarn build
```

Edit landing page sources under `landing_page/src/`. React application sources live under `frontend/src/`; backend tools live under `tools/`.

## Make and validate changes

Follow the surrounding code style and keep changes focused. Update relevant documentation and translations when behavior or user-facing text changes. Add regression coverage for substantive behavior changes where practical.

Run checks relevant to your change:

- For backend changes, check Python syntax and exercise the affected endpoints against a local development instance.
- The tests under `tests/` call a running server at `http://localhost:5000/api`; review their authentication and data requirements before running them.
- For frontend changes, run `yarn test --watchAll=false` from `frontend/` and check the affected screens manually.
- To validate a frontend production bundle locally, run `yarn exec react-scripts build` from `frontend/`. The package's `yarn build` script also uploads source maps to Sentry and requires the appropriate service configuration.
- For landing page changes, run `yarn build` from `landing_page/` and inspect the result.

Describe checks you could not run and any setup limitations in your pull request.

## Submit a pull request

Use a descriptive title and explain the problem, the resulting behavior, and how you validated it. Link related issues and include screenshots for visible interface changes. Avoid unrelated formatting changes, generated files unrelated to your change, and local configuration files.

Respond to review feedback and keep discussion respectful and constructive.

## License

By submitting a contribution, you agree to license your original contribution under the project's [GNU Affero General Public License version 3](LICENSE.md) (`AGPL-3.0-only`). Only submit material you have permission to contribute, and preserve applicable copyright and license notices.
