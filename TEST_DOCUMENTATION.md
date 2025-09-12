# Test Suite Documentation for `webscrape.py`

This document provides detailed documentation for each test in the `test_webscrape.py` test suite. The test suite contains **33 comprehensive tests** covering all functions and edge cases in the amateur radio repeater scraping application.

## Table of Contents

1. [Form Data Tests](#form-data-tests)
2. [Repeater Data Processing Tests](#repeater-data-processing-tests)
3. [Frequency Offset Tests](#frequency-offset-tests)
4. [Output Filtering Tests](#output-filtering-tests)
5. [CHIRP Format Tests](#chirp-format-tests)
6. [Main Function Integration Tests](#main-function-integration-tests)
7. [Digital Mode Tests](#digital-mode-tests)
8. [Edge Case Tests](#edge-case-tests)

---

## Form Data Tests

### 1. `test_updatewebformdata()`
**Purpose**: Tests the basic functionality of updating web form data with search parameters.

**What it tests**:
- Function correctly combines city and state into location field
- Appends comma to bands string for form submission
- Updates existing form data dictionary without overwriting existing keys
- All form fields are populated correctly

**Test Data**:
- City: "TestCity"
- State: "TS" 
- Radius: "100"
- Bands: "144,440"

**Expected Results**:
- `loca`: "TestCity, TS"
- `radi`: "100" 
- `band`: "144,440," (note trailing comma)
- `freq`: "1per"
- `dbfilter`: "neny"
- Existing keys preserved

---

### 2. `test_updatewebformdata_empty_inputs()`
**Purpose**: Tests how the function handles empty or minimal input values.

**What it tests**:
- Function doesn't crash with empty strings
- Empty values are handled gracefully
- Form structure is maintained even with no data

**Test Data**: All empty strings

**Expected Results**:
- `loca`: ", " (comma and space for empty city/state)
- `radi`: ""
- `band`: "," (just comma for empty bands)
- Other fields empty

---

## Repeater Data Processing Tests

### 3. `test_processrepeaterdata_basic_fm()`
**Purpose**: Tests processing of a basic FM analog repeater entry.

**What it tests**:
- City/state parsing from "City, ST" format
- Frequency extraction and storage
- FM mode detection from PL tone presence
- CTCSS tone extraction
- Basic repeater data structure creation

**Test Data**: FM repeater with 100.0 Hz CTCSS tone on 145.0 MHz

**Expected Results**:
- City: "City", State: "ST"
- Frequency: 145.0
- Call sign: "CALL"
- FM mode: "TRUE"
- CTCSS: "100.0"

---

### 4. `test_processrepeaterdata_ysf_mode()`
**Purpose**: Tests YSF (System Fusion) digital mode detection and AMS mode configuration.

**What it tests**:
- YSF mode detection from PL field
- AMS mode v2 configuration (vs v1)
- Operating mode set to "FM" for v2
- AMS flag set to "Y" for v2

**Test Data**: YSF repeater with "v2" AMS mode

**Expected Results**:
- YSF mode: "TRUE"
- Operating Mode: "FM" (for v2)
- AMS: "Y" (for v2)

---

### 5. `test_processrepeaterdata_chirp_output()`
**Purpose**: Tests CHIRP format output generation for radio programming software.

**What it tests**:
- CHIRP entry creation when chirp=True
- Proper CHIRP field mapping
- Frequency conversion to string
- Tone configuration for CHIRP format

**Test Data**: FM repeater with CHIRP output enabled

**Expected Results**:
- CHIRP entry created in chirprepeaterlist
- Location: "0" (first entry)
- Name: "CALL"
- Frequency: "145.0" (as string)
- Tone: "Tone"
- rToneFreq: "100.0"

---

### 6. `test_processrepeaterdata_search_filter()`
**Purpose**: Tests search filtering functionality to find specific repeaters.

**What it tests**:
- Search filter matches entries containing specified text
- Case-sensitive search behavior
- Non-matching entries are excluded
- Dual test: matching and non-matching scenarios

**Test Data**: 
- Repeater with "NB1RI Notes" 
- Search for "NB1RI" (should match)
- Search for "NoMatch" (should not match)

**Expected Results**:
- First search: 1 result
- Second search: 0 results

---

### 7. `test_processrepeaterdata_nan_handling()`
**Purpose**: Tests handling of NaN (Not a Number) values from pandas DataFrames.

**What it tests**:
- NaN values converted to "EMPTY" string
- Processing continues without errors
- All fields handle missing data gracefully

**Test Data**: Repeater entry with float("nan") in multiple fields

**Expected Results**:
- City: "EMPTY"
- State: "EMPTY" 
- Frequency: "EMPTY"
- Call: "EMPTY"

---

### 8. `test_processrepeaterdata_dcs_code()`
**Purpose**: Tests Digital Coded Squelch (DCS) detection and parsing.

**What it tests**:
- DCS code extraction from "DCS(023)" format
- FM mode enabled when DCS detected
- Tone mode set to "DCS"
- DCS code padded to 3 digits

**Test Data**: Repeater with "DCS(023)" in notes

**Expected Results**:
- FM: "TRUE"
- DCS: "023"
- Tone Mode: "DCS"

---

### 9. `test_processrepeaterdata_extended_notes()`
**Purpose**: Tests extended notes functionality for detailed repeater information.

**What it tests**:
- Extended notes format: "City,State,Call,Notes"
- exnotes flag enables extended format
- Comma-separated concatenation

**Test Data**: Repeater with exnotes=True

**Expected Results**:
- Comment field: "City,ST,CALL,Extra Notes"

---

## Digital Mode Tests

### 10. `test_processrepeaterdata_digital_modes_comprehensive()`
**Purpose**: Tests DMR (Digital Mobile Radio) detection and Color Code extraction.

**What it tests**:
- DMR mode detection from PL field
- Color Code extraction from notes using regex pattern `[C]{2,4}[0-9]{1,2}`
- Proper CC field population

**Test Data**: DMR repeater with "CCC1" color code

**Expected Results**:
- DMR: "TRUE"
- DMR CC: "CCC1"

---

### 11. `test_processrepeaterdata_p25_with_nac()`
**Purpose**: Tests P25 digital mode and Network Access Code (NAC) extraction.

**What it tests**:
- P25 mode detection from PL field
- NAC extraction from "NAC293" format
- NAC field includes "NAC " prefix

**Test Data**: P25 repeater with "NAC293"

**Expected Results**:
- P25: "TRUE"
- P25 NAC: "NAC 293"

---

### 12. `test_processrepeaterdata_nxdn_with_ran()`
**Purpose**: Tests NXDN digital mode and Radio Access Number (RAN) extraction.

**What it tests**:
- NXDN mode detection from PL field
- RAN extraction from "RAN01" format using regex `RAN[0-9]{1,2}`
- Full RAN string preservation

**Test Data**: NXDN repeater with "RAN01"

**Expected Results**:
- NXDN: "TRUE"
- NXDN RAN: "RAN01"

---

### 13. `test_processrepeaterdata_dstar_mode()`
**Purpose**: Tests D-STAR digital mode detection.

**What it tests**:
- D-STAR mode detection from "D-STAR" in PL field
- Simple boolean flag setting

**Test Data**: D-STAR repeater

**Expected Results**:
- D-STAR: "TRUE"

---

### 14. `test_processrepeaterdata_tone_edge_cases()`
**Purpose**: Tests various tone configurations and edge cases.

**What it tests**:
- Valid PL tones (67.0 Hz)
- Carrier squelch (CSQ) handling
- Empty tone fields
- Split tones (100.0/110.0) - takes first valid tone
- DTCS without code

**Test Cases**:
1. "67.0" → tone: "67.0", mode: "Tone"
2. "CSQ" → tone: "", mode: ""
3. "" → tone: "", mode: ""
4. "100.0/110.0" → tone: "100.0", mode: "Tone"
5. "DTCS" → tone: "", mode: ""

---

### 15. `test_processrepeaterdata_frequency_parsing()`
**Purpose**: Tests frequency parsing and storage in various formats.

**What it tests**:
- Frequencies stored as strings (not converted to float)
- Various decimal formats preserved
- No data loss in conversion

**Test Cases**:
- "145.000" → "145.000"
- "145.5" → "145.5"
- "442.000" → "442.000"
- "52.525" → "52.525"

---

### 16. `test_processrepeaterdata_distance_direction_parsing()`
**Purpose**: Tests distance and direction parsing from "DIST/DIR" field.

**What it tests**:
- Regex extraction of distance and direction
- Pattern: `([0-9]{1,3}.[0-9])([EWNS][EW]{0,1}|)`
- Separate distance and direction fields

**Test Cases**:
- "10.5N" → distance: "10.5", direction: "N"
- "25.0SW" → distance: "25.0", direction: "SW"
- "5.2E" → distance: "5.2", direction: "E"
- "100.0NE" → distance: "100.0", direction: "NE"

---

## Frequency Offset Tests

### 17. `test_determineoffset_various_bands()`
**Purpose**: Tests offset calculation for different amateur radio frequency bands.

**What it tests**:
- 6m band: 51.5 MHz → -0.5 MHz
- 2m band: 145.2 MHz → -0.6 MHz, 147.1 MHz → +0.6 MHz
- 1.25m band: 224.0 MHz → -1.6 MHz
- 70cm band: 442.0 MHz → +5.0 MHz, 447.0 MHz → -5.0 MHz
- 33cm band: 920.0 MHz → -12.0 MHz, 927.5 MHz → -25.0 MHz

**Expected Results**: Correct offset values and directions for each band

---

### 18. `test_determineoffset_comprehensive_coverage()`
**Purpose**: Comprehensive testing of all frequency ranges and edge cases.

**What it tests**:
- **6m Band (50-54 MHz)**:
  - Below range: 50.5 MHz → 0, "off"
  - 51.0-51.99 MHz → -0.5, "-"
  - 52.0-54.0 MHz → -1.0, "-"
  - Above range: 54.1 MHz → 0, "off"

- **2m Band (144-148 MHz)** - Complex ranges:
  - 144.51-144.89 MHz → +0.6, "+"
  - 145.11-145.49 MHz → -0.6, "-"
  - 146.0-146.39 MHz → +0.6, "+"
  - 146.4-146.5 MHz → -1.5, "-" (special range)
  - 146.61-146.99 MHz → -0.6, "-"
  - 147.0-147.39 MHz → +0.6, "+"
  - 147.6-147.99 MHz → -0.6, "-"

- **1.25m Band (222-225 MHz)**:
  - 223.0-225.0 MHz → -1.6, "-"

- **70cm Band (440-450 MHz)**:
  - 440-444.99 MHz → +5.0, "+"
  - 445-450 MHz → -5.0, "-"

- **33cm Band (900+ MHz)**:
  - 918-922 MHz → -12.0, "-"
  - 927-928 MHz → -25.0, "-"

---

### 19. `test_determineoffset_invalid()`
**Purpose**: Tests handling of invalid frequency inputs.

**What it tests**:
- Non-numeric strings return 0, "off"
- Out-of-band frequencies return 0, "off"
- Error logging for invalid inputs

**Test Cases**:
- "EMPTY" → 0, "off"
- "0.0" → 0, "off"
- "1000.0" → 0, "off"
- "invalid" → logs error, returns 0, "off"

---

### 20. `test_determineoffset_error_handling()`
**Purpose**: Tests comprehensive error handling for malformed frequency strings.

**What it tests**:
- Various invalid formats trigger proper error logging
- Function returns safe default values
- No crashes on bad input

**Test Cases**:
- "not_a_number"
- "abc.def"
- "" (empty string)
- "  " (whitespace)
- "145.abc"
- "145..0" (double decimal)
- "145,0" (wrong decimal separator)

**Expected Results**: All return 0, "off" with error logged

---

## Output Filtering Tests

### 21. `test_filteroutput_multiple_modes()`
**Purpose**: Tests filtering repeaters by multiple mode criteria.

**What it tests**:
- Multiple mode filters work with OR logic
- "all" filter bypasses mode checking
- Proper field indices for each mode

**Test Data**: Repeater with FM and YSF enabled

**Test Cases**:
1. Filter ["fm", "ysf"] → 1 result (matches)
2. Clear modes, filter ["fm", "ysf"] → 0 results
3. Filter ["all"] → 1 result (always matches)

---

### 22. `test_filteroutput_single_mode()`
**Purpose**: Tests filtering for individual digital modes.

**What it tests**:
- Single mode filtering (DMR)
- Field index 13 for DMR mode
- Boolean matching logic

**Test Data**: Repeater with DMR enabled/disabled

**Expected Results**:
- DMR enabled → 1 result
- DMR disabled → 0 results

---

### 23. `test_filteroutput_all_digital_modes()`
**Purpose**: Tests filtering capability for all supported digital modes.

**What it tests**:
- All 6 digital modes can be filtered individually
- Correct field indices for each mode:
  - FM: index 9
  - DMR: index 13
  - NXDN: index 15
  - P25: index 17
  - D-STAR: index 19
  - YSF: index 20

**Test Data**: Repeater with all modes enabled

**Expected Results**: Each mode filter returns 1 result

---

### 24. `test_filteroutput_mixed_mode_combinations()`
**Purpose**: Tests complex combinations of mode filters.

**What it tests**:
- Multiple mode combinations with OR logic
- Edge cases where repeater has some but not all modes

**Test Data**: Repeater with FM, DMR, and YSF enabled

**Test Combinations**:
1. ["fm", "dmr"] → True (has both)
2. ["fm", "ysf"] → True (has both)
3. ["dmr", "ysf"] → True (has both)
4. ["fm", "dmr", "ysf"] → True (has all)
5. ["nxdn", "p25"] → False (has neither)
6. ["dstar"] → False (doesn't have)

---

## CHIRP Format Tests

### 25. `test_chirpbuild()`
**Purpose**: Tests basic CHIRP entry building functionality.

**What it tests**:
- CHIRP entry appended to list correctly
- Data structure preserved
- Simple append operation

**Test Data**: Complete CHIRP entry with all 18 fields

**Expected Results**: Entry added to chirprepeaterlist

---

### 26. `test_chirpbuild_multiple_entries()`
**Purpose**: Tests building multiple CHIRP entries for batch operations.

**What it tests**:
- Multiple entries can be added sequentially
- Each entry maintains its data integrity
- List indexing works correctly

**Test Data**: 3 CHIRP entries with incrementing data

**Expected Results**:
- 3 entries in list
- Each entry has correct location index and call sign

---

## Main Function Integration Tests

### 27. `test_main_basic()`
**Purpose**: Tests basic main function operation with minimal parameters.

**What it tests**:
- Command-line argument parsing
- HTTP request mocking
- HTML table parsing
- CSV file output
- Integration of all components

**Mocked Components**:
- `requests.Session.post()` → returns mock HTML
- `pandas.read_html()` → returns mock DataFrame
- `builtins.open()` → captures file operations
- `sys.argv` → provides test arguments

**Expected Results**: Output file "repeaters.csv" created

---

### 28. `test_main_debug_logging()`
**Purpose**: Tests debug mode functionality and logging configuration.

**What it tests**:
- Debug flag (-d) enables detailed logging
- Logging configuration is properly set up
- Debug information is captured

**Test Data**: Debug mode enabled with -d flag

**Expected Results**: Function runs without errors in debug mode

---

### 29. `test_main_error_handling()`
**Purpose**: Tests error handling for network failures and exceptions.

**What it tests**:
- Network request failures are caught
- System exits gracefully on errors
- Error logging occurs

**Test Scenario**: Mock network request raises RequestException

**Expected Results**: SystemExit raised (graceful shutdown)

---

### 30. `test_main_with_all_options()`
**Purpose**: Tests main function with comprehensive command-line options.

**What it tests**:
- All command-line options parsed correctly
- Complex option combinations work
- Custom output file naming
- Mode filtering integration
- CHIRP output generation

**Command Line Options Tested**:
- `-c Boston` (city)
- `-s MA` (state)  
- `-r 50` (radius)
- `-b 144,440` (bands)
- `-o test_output.csv` (output file)
- `-f ysf,dmr` (mode filter)
- `-k` (one per frequency)
- `-p` (CHIRP output)
- `-q nesmc` (database filter)
- `-x` (extended notes)
- `-a v2` (AMS mode)

**Expected Results**: Custom output file created

---

### 31. `test_main_input_validation()`
**Purpose**: Tests input validation and error handling for invalid arguments.

**What it tests**:
- Invalid radius (non-numeric) → SystemExit
- Invalid frequency bands → SystemExit  
- Invalid state format → SystemExit
- Proper error messages displayed

**Test Cases**:
1. Radius: "invalid" → ArgumentParser error
2. Bands: "999" → "Invalid bands" error
3. State: "MASS" → "State must be a two-letter code" error

**Expected Results**: All cases raise SystemExit

---

### 32. `test_main_database_filters()`
**Purpose**: Tests all available database filter options.

**What it tests**:
- All 6 database filters work correctly:
  - "nerep" (New England Repeater Directory)
  - "nesmc" (New England Spectrum Management Council)
  - "csma" (Connecticut Spectrum Management Association)
  - "nyrep" (New York Repeater Directory)
  - "nesct" (New England + Connecticut combined)
  - "neny" (New England + New York combined)

**Test Method**: Each filter tested in isolation with mocked responses

**Expected Results**: All database filters execute without errors

---

## Edge Case Tests

### 33. `test_processrepeaterdata_edge_case_inputs()`
**Purpose**: Tests edge cases and minimal data scenarios.

**What it tests**:
- Minimal valid data (empty fields but valid city/state format)
- Processing continues with sparse data
- No crashes on missing information

**Test Data**: Repeater with only "City, ST" and empty other fields

**Expected Results**: 1 repeater processed without errors

---

## Test Infrastructure

### Mocking Strategy
The test suite uses `unittest.mock` extensively to isolate components:

- **Network Requests**: `requests.Session.post()` mocked to avoid external dependencies
- **File Operations**: `builtins.open()` mocked to capture file I/O without actual files
- **HTML Parsing**: `pandas.read_html()` mocked with controlled DataFrame responses
- **Command Line**: `sys.argv` patched to provide test arguments
- **Logging**: `logging.basicConfig()` mocked to avoid log file creation

### Test Data Patterns
- **Repeater Data Structure**: 7-element lists representing raw scraper data
- **Expected Output Structure**: 25-element lists representing processed repeater data
- **CHIRP Data Structure**: 18-element lists for radio programming format
- **Mock HTML**: Realistic HTML table structure matching actual scraper targets

### Assertion Strategies
- **Length Checks**: Verify correct number of results
- **Field Validation**: Check specific data fields at known indices
- **Error Conditions**: Use `assertRaises()` for expected failures
- **Logging Verification**: Use `assertLogs()` to verify error messages
- **Mock Verification**: Check that mocked functions were called correctly

### Coverage Analysis
The test suite provides comprehensive coverage:
- **Function Coverage**: All 6 main functions tested
- **Branch Coverage**: Major code paths and conditions tested
- **Error Coverage**: Exception handling and edge cases tested
- **Integration Coverage**: End-to-end workflows tested
- **Data Coverage**: All data types and formats tested

This test suite ensures robust validation of the amateur radio repeater scraping application, providing confidence in code reliability and maintainability.

