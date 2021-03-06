# =============================================================================
# codePost – Brightspace Utility
#
# Takes submissions downloaded from Brightspace and transforms the file structure
# into a structure that codePost will recognize.
#
# =============================================================================

# Python stdlib imports
import os
import argparse
import csv
import shutil
import re

# =============================================================================

parser = argparse.ArgumentParser(description='Brightspace to codePost!')
parser.add_argument(
    'submissions', help='The directory of submissions downloaded from Brightspace')
parser.add_argument(
    'roster', help='The course roster of students that includes first name, last name, and email')
parser.add_argument('-s', '--simulate', action='store_true', help="Use to simulate the script without copying anything")
parser.add_argument('-f', '--folders', action='store_true', help="Use when the submissions are downloaded in folders")
args = parser.parse_args()

# =============================================================================
# Constants

OUTPUT_DIRECTORY = 'codepost_upload'
ERROR_DIRECTORY = 'errors'
TEMP_DIRECTORY = 'temp'

_cwd = os.getcwd()
_upload_dir = os.path.join(_cwd, OUTPUT_DIRECTORY)
_error_dir = os.path.join(_cwd, ERROR_DIRECTORY)
_temp_dir = os.path.join(_cwd, TEMP_DIRECTORY)

# =============================================================================
# Helpers


def normalize(string):
  return string.lower().strip()


def delete_directory(path):
  if os.path.exists(path):
    shutil.rmtree(path)


def validate_csv(row):
  for key in row.keys():
    if 'first' in normalize(key):
      first = key
    elif 'last' in normalize(key):
      last = key
    elif 'email' in normalize(key):
      email = key

  if first == None or last == None or email == None:
    if first == None:
      print("Missing header: first")
    if last == None:
      print("Missing header: last")
    if email == None:
      print("Missing header: email")

    raise RuntimeError(
        "Malformatted roster. Please fix the headers and try again.")

    return (first, last, email)
  else:
    return (first, last, email)


def name_to_email(roster):
  with open(roster, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    first, last, email = (None, None, None)
    name_to_email = {}
    for row in csv_reader:
      if line_count == 0:
        (first, last, email) = validate_csv(row)
        line_count += 1

      # Brightspace convention: map {firstname} {lastname} to {codePost email}
      name_to_email["{} {}".format(
          normalize(row[first]), normalize(row[last]))] = normalize(row[email])
      line_count += 1
    return name_to_email


def check_for_partners(file_name):
  submissions_folder = args.submissions if False else _temp_dir
  filepath = os.path.join(submissions_folder, file_name)
  emails = [line.rstrip('\n') for line in open(filepath, 'r')]
  EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"
  filtered_emails = [x for x in emails if re.match(EMAIL_REGEX, x)]

  return filtered_emails

# =============================================================================

if (args.simulate):
  print('\n~~~~~~~~~~~ START SIMULATION ~~~~~~~~~~~')

print('\nSetting up directories...')

# Overwrite the directories if they exist already
if not args.simulate:
  delete_directory(_upload_dir)
  delete_directory(_error_dir)

  os.makedirs(_upload_dir)
  os.makedirs(_error_dir)

  if args.folders:
    delete_directory(_temp_dir)
    os.makedirs(_temp_dir)

print('\t/{}'.format(OUTPUT_DIRECTORY))
print('\t/{}'.format(ERROR_DIRECTORY))

print('\nReading and validating roster...')
name_to_email = name_to_email(args.roster)
print('\tVALID')

print('\nChecking submissions for partners...')

if args.folders:
  sub_folders = [x[0] for x in os.walk(args.submissions)][1:]
  for sub_folder in sub_folders:
    contents = os.listdir(sub_folder)
    for sub_file in contents:
      # print()
      # print(os.path.join(_temp_dir, sub_folder + ' - ' + sub_file))
      shutil.copyfile(os.path.join(sub_folder, sub_file), os.path.join(
          _temp_dir, sub_folder.split('/')[-1] + ' - ' + sub_file))
  files = os.listdir(_temp_dir)
else:
  files = os.listdir(args.submissions)

folders = []
for file in files:
  file_name = file.split('-')[-1]
  if 'partners' in file_name:
    partners = check_for_partners(file)
    folders.append(partners)

print('\t{}'.format(folders))

print('\nCreating student folders...')
for student in name_to_email:
  found = False
  for folder in folders:
    if name_to_email[student] in folder:
      found = True
      break

  if not found:
    folders.append([name_to_email[student]])

for folder in folders:
  folder_name = ",".join(folder)
  if not args.simulate:
    os.makedirs(os.path.join(_upload_dir, folder_name))
  print('\t{}'.format(folder_name))


print('\nMapping and copying files...')
submissions_folder = _temp_dir if args.folders else args.submissions
for file in files:
  if len(file.split('-')) > 3:
    student_name = file.split('-')[2].strip()
    file_name = file.split('-')[-1].strip()

    if normalize(student_name) in name_to_email:
      email = name_to_email[normalize(student_name)]
      found = False

      for folder in folders:
        if email in folder:
          folder_name = ",".join(folder)
          found = True
          if not args.simulate:
            try:
              shutil.copyfile(os.path.join(submissions_folder, file), os.path.join(
                  os.path.join(_upload_dir, folder_name), file_name))
            except IsADirectoryError:
              raise Exception("ERROR: [{}] is a directory. Try using the --folders command line flag. For help run: python3 brightspace_to_codepost_manual.py --help".format(
                  file))
          print('\t{}'.format(os.path.join(
              os.path.join(_upload_dir, folder_name), file_name)))

      if not found:
        if not args.simulate:
          shutil.copyfile(os.path.join(submissions_folder, file),
                          os.path.join(_error_dir, file))
        print('\tERROR: {}'.format(os.path.join(_error_dir, file)))
    else:
      if not args.simulate:
        shutil.copyfile(os.path.join(submissions_folder, file),
                        os.path.join(_error_dir, file))
      print('\tERROR: {}'.format(os.path.join(_error_dir, file)))

if args.folders:
  delete_directory(_temp_dir)

if args.simulate:
  print('\n~~~~~~~~~~~ END SIMULATION ~~~~~~~~~~~\n')
