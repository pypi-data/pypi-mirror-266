# umdsubmit

This package allows submitting to the UMD Submit Server from the command line, without the Eclipse Plugin.

## Installation

You can install the package via pip:

```sh
pip install umdsubmit
```

## Updating

The package can be upgraded via pip:

```sh
pip install umdsubmit --upgrade
```

## Usage

After installing navigate to the root of the project directory in the terminal and run the command umdsubmit. Enter your UMD Directory ID and password as requested. Ensure that you run the command from the directory containing the .submit file for the project.

## How It Works

1. **Initialization:**
   - The `umdsubmit` command is executed, initiating the submission process.

2. **Zip Archive Creation:**
   - The `shutil.make_archive` function is used to create a zip archive of the current working directory.

3. **File Reading - .submit:**
   - The `get_info` function is called to gather necessary submission data from the `.submit` file in the current directory.

4. **CVS Account Retrieval:**
   - The `get_cvs_account` function is called to obtain the CVS account.
   - If the `.submitUser` file exists, it is read to get the account information.
   - If the file doesn't exist, the `auth` function is triggered to authenticate the user, which creates a `.submitUser` file storing information for later submissions.
  
5. **User Authentication (if needed):**
   - The `auth` function prompts the user to enter their UMD Directory ID and password.
   - A POST request is made to the server to negotiate a one-time password.
   - The server's response is written to the `.submitUser` file and printed to the console.

6. **Submission:**
   - A POST request is made to the submit URL with the zip file and the gathered data.
   - The server's response is printed to the console.
