# sc-client-python

A python client for the Software-Challenge Germany.

## Creating a new project

- (Optional) Install virtualenv

  `virtualenv` is a tool that creates a local python enviroment.

  It is useful if you have two projects that require different versions of the same package which can happen really often.

  ```
  pip install virtualenv
  ```

- (Optional) Use virtualenv

  Execute `virtualenv venv` to create a new local python enviroment and execute `source venv/bin/activate` to enter it (on windows `venv\Scripts\activate`).

- Install sc-client-python

  Execute:

  ```
  pip install git+https://github.com/rpkak/sc-client-python@tag
  ```

  where `tag` is the version of sc-client-python, `master` to get the latest unstable version or `latest` to get the latest stable version.

- Create an empty project

  To create an empty project just execute:

  ```
  scpy init
  ```

  If you don't want to create a git repository, execute:

  ```
  scpy init --no-git
  ```

  Now you have a project which does not have any intelligence, but always uses the first possible step.

- Run the client

  To run the client just execute while the server is running:

  ```
  scpy run
  ```

## Configurations

To see more configurations execute `scpy init --help` and `scpy run --help`.

Documentation is (maybe) coming soon.
