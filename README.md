# Dotacni pomucka

This repository contains the source files for the Dotacni pomucka app made for the MxB corporation. This app is meant to
help accountants with filing government support claims for companies employing the disabled and elderly.

The project itself is written entirely in Python utilising the customTkinter library for rendering the GUI and pandas 
for Excel sheet processing. The project also utilises the requests library for downloading the government template for 
government support claims. ExcelWings is also utilised to perform dark Excel magic on the file since it is a xlsm, 
meaning it contains embedded macros that pandas cannot force to run.

The documentation for this project may be generated via mounting the docs directory and running `make html` on Unix
based systems or running `make.bat html` on Windows machines. You may then navigate to the `_build/html` subdirectory
and open the `index.html` file, which will contain all the documentation for this project.

## Project goals

The main goal of this project is to provide proprietary software to the MxB corporation for utilisation in the finance
industry in order to speed up work processes undertaken by accountants. In the case of this software mainly during
calculating the amount of state subsidies a company may claim for employing disabled persons.

## Project structure

The project is broken up into multiple packages, each containing files with common functionality.

### Dotacovatko

The Dotacovatko package contains the main app class, which initialises all the required components, handles GUI 
rendering and background process communication.

### Enums

The Enums package contains all the enums that the app utilises during runtime, these enums are, in no particular order:

* `ColourEnum` - Containing colour hex code definitions for the GUI.
* `DisabilityStatusEnum` - Containing official Czech disability statuses.
* `EmployeeDataHeaders` - Containing the headers utilised during data processing for ordering.
* `EmployeeInputHeaders` - Containing headers present inside the government template sheet.
* `ErrNoEnum` - Containing all the different error codes that can be raised by the app.
* `HumanResourcesHeaders` - Containing an enum with the headers present in the human resources sheet expected from the user.
* `MonthEnum` - Containing the months of the year in text form.
* `MonthHeaders` - Containing headers present in the input month sheets, expected from the user.
* `QuarterEnum` - Containing the quarters of the year represented by ints.
* `QueueStatus` - Containing all possible status messages that may be sent by either the GUI or the background process.
* `TemplateSheetNames` - Containing all the sheet names present in the government template workbook. 

These mainly help with code clarity, so the code is not filled to the brim with magic numbers, strings and whatnot else.

### Mappers

The Mappers package contains mappers utilised when a value needs to be utilised to infer another one. All the classes 
within usually contain the bare minimum for this functionality, an `_MAPPING` class attribute containing the dictionary
with the mappings and then a single class method used to invoke this dictionary and map the passed value.

### Services

The Services package contains classes that provide the background processing capability to the app.

#### ExcelProcessor

This class provides all the capabilities for processing the passed input Excel file in several different methods. It
also contains a `run` method that invokes these processing methods and sends messages back to the GUI with information
about the progress of the processing, this is done mainly so the progressbar actually progresses with the processing.
`ExcelProcessor` works in tandem with the `TemplateManager` to which it hands over the responsibility for preprocessing
the government workbook and writing data into it, since utilising pandas for all of this would break the template.

#### TemplateManager

This class provides the functionality required for interfacing with the government Excel Workbook template itself. Since
the template is filled with formulas and macros (some of them breaking `openpyxl`) a very specific dark magic approach is
required. It utilises the `xlwings` library to reload the template when a macro needs to be executed in order for the
template to automatically change itself according to data input into it. Along with this before even opening the
template it utilises the `zipfile`, `io` and other such libraries to sanitise the template before performing any kind of
operations with it. This is done because the template itself contains an error, which Excel overlooks, `openpyxl` however
does not.

Otherwise, this class performs all read/write operations on the workbook and handles general io with the template. Thus 
whenever anything should be written into the template the `write_into_cell` method should be utilised.

### Utils

The Utils package contains all the utility data structures and classes utilised in the application. These utilities
range from simple GUI helpers for displaying basic information to the user (`SuccessHandler`, `ErrorHandler`) to
handling file pathing within the system (`ResourceFinder`) or custom errors (`AppError`).

### Widgets

The Widgets package contains all the GUI elements each contained in their own class. These mostly just set initial
values for the underlying `customtkinter` widgets they inherit from during initialisation. Mainly they set up the basic
look of the GUI widget (setting colour to be within the MxB colour scheme and such).

## Usage

The app can either be packaged using the `pyinstaller` library by mounting into the folder with the project and running
`pyinstaller .\dotacovatko.spec`. The `.spec` file contains all the necessary directive and pyinstaller will be able to
package the project into a `.exe` file compatible with Windows. Ensuring MAC distributable packaging is currently not
planned. By default, the packaging method ensures a single file `.exe` with no terminal attached during runtime.

The application may also be run by mounting into the folder containing the project and running `python main.py` which
will start up the application.

## Requirements

For requirements, please check the `requirements.txt` file or consult the `pyproject.toml` file. This project was
assembled using `uv` this it is compatible with it and `uv` may be utilised to fetch all requirements.
