# HWDOCER releases

See what is planned in the [roadmap][roadmap_file]

## 0.2.2

Release date: _2024-04-09_

**Feature:**

- progress bar now displayed in the console
- added an argument to display software version

**Fix:**

- Segregated file searching and file copying into 2 steps

**Known problem:**

- leave failed graphviz file without extension in _output folder_ when wireviz syntax is invalid
- file copy fails to replicate the correct folder structure whit some input (media at same level as subfolder)

## 0.2.1

Release date: _2024-04-04_

**Feature:**

- change console output to rich python lib for better logging
- minimal work stat printed & logged at execution end

**Fix:**

- change wireviz call to run and hopefully get more helpful verbose error (not much info from wireviz itself)

**Known problem:**

- leave failed graphviz file without extension in _output folder_ when wireviz syntax is invalid
- file copy fails to replicate the correct folder structure whit some input (media at same level as subfolder)

## 0.2.0

Release date: _2024-04-03_

**Feature:**

- automatic removal of undesired file format (wireviz) in output folder (multiple can be kept via `--hrs` args)

**Fix:**

- wrapped wireviz and drawio call in silent subprocess to handle console pollution (unknown exception will still be raised)

**Known problem:**

- leave failed graphviz file without extension in _output folder_ when wireviz syntax is invalid
- file copy fails to replicate the correct folder structure whit some input (media at same level as subfolder)

## 0.1.4

Release date: _2024-04-02_

**Feature:**

- source files are now copied in output folder
- refactor the execution to be file based instead of process based
- all building is now executed in isolated multiprocessor-compatible processes
- added argument to control the number of processes created
- added argument to limit the execution time
- added argument to control the output files format (present but not used yet)

**Fix:**

- image from harnesses are now correctly copied into a similar folder structure inside output folder

**Known problem:**

- **[corrected in 0.2.0]** drawio calls throws some error in console and logs
- **[corrected in 0.2.0]** wireviz bad syntax throws stacktrace in console and logs
- **[corrected in 0.2.0]** leave a lot of undesired generated files in input and output folders
- leave failed graphviz file without extension in _output folder_ when wireviz syntax is invalid

## 0.1.3

Release date: _2024-03-27_

**Feature:**

- copy all images defined in harness with tag `image`.`src` to output path (for html correct render)

**Known problem:**

- **[corrected in 0.2.0]** drawio calls throws some error in console and logs
- **[corrected in 0.2.0]** wireviz bad syntax throws stacktrace in console and logs
- **[corrected in 0.1.4]** image copy doesn't recreate sub-folder structure into output destination
- **[corrected in 0.2.0]** leave a lot of undesired generated files in input and output folders
- leave failed graphviz file without extension in _output folder_ when wireviz syntax is invalid

## 0.1.2

Release date: _2024-03-27_

**Feature:**

- Improve debug verbosity
- Input file search is more iterative now

**Change:**

- Changed input file search to use glob instead of os.walk

**Known problem:**

- **[corrected in 0.2.0]** drawio calls throws some error in console and logs
- **[corrected in 0.2.0]** wireviz bad syntax throws stacktrace in console and logs
- **[corrected in 0.2.0]** leave a lot of undesired generated files in input and output folders
- leave failed graphviz file without extension in _output folder_ when wireviz syntax is invalid

## 0.1.1

Release date: _2024-03-26_

**Fix:**

- Project publishing metadata added/corrected

**Known problem:**

- **[corrected in 0.2.0]** drawio calls throws some error in console and logs
- **[corrected in 0.2.0]** wireviz bad syntax throws stacktrace in console and logs
- **[corrected in 0.2.0]** leave a lot of undesired generated files in input and output folders
- leave failed graphviz file without extension in _output folder_ when wireviz syntax is invalid

## 0.1.0

Release date: _2024-03-26_

**Feature:**

- Initial functional release
- development venv setup
- logging in multiprocessing thread
- drawio automatic drawing via system call
- wireviz automatic drawing
- basic functional test for diagram and harness
- selectable verbosity in console and log (one argument for both)
- buildable & deployable with poetry

**Known problem:**

- **[corrected in 0.2.0]** drawio calls throws some error in console and logs
- **[corrected in 0.2.0]** wireviz bad syntax throws stacktrace in console and logs
- **[corrected in 0.2.0]** leave a lot of undesired generated files in input and output folders
- leave failed graphviz file without extension in _output folder_ when wireviz syntax is invalid

---

[roadmap_file]: roadmap.md
