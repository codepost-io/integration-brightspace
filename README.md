# Integrating with Brightspace

This repository contains short utility scripts that make it easy to connect codePost with Brightspace. To learn more about codePost, check out the [the codePost website](https://codepost.io). 

A typical lead instructor will usually do something like the following every week:

- Import student submissions into codePost from Brightspace
- Grade and review student submissions in codePost
- Export grades from codePost back to Brightspace in a csv

# Import submissions into codePost from Brightspace

First, we’ll download assignment submissions from Brightspace to our local machine.

Next, we’ll run `brightspace_to_codepost_manual` script, which will create a folder called `codepost_upload` which you can drag-and-drop into codePost. Any errors will show up in the `errors` folder.

The process will only take a minute, start to finish.

> Need help? Email us at team@codepost.io

## 0. Downloading Submissions from Brightspace

In your Brightspace Instance Original Course View, to `Course -> Assignments -> <Assignment> -> <Select All> -> Download`

## 1. Create a roster

Since the Brightspace downloads are indexed by Student Name, we need to map {Student Name} to {Email} in order to upload to codePost.

Create a roster.csv with the following information:

```
first,last,email
alan,turing,turing@school.edu
barbara,liskov,liskov@school.edu
sheldon,cooper,cooper@school.edu
```

## 2. Setting up the script

Clone this repository or copy the python script `brightspace_to_codepost_manual.py` to your local machine.

Move the downloaded submissions into the same directory as the script and name the folder `submissions`.

Move the roster.csv file you created into the same directory as the script. Make sure this file is called `roster.csv.`

## 3. Run the script

Make sure that you have Python3 installed and run

`python3 brightspace_to_codepost_manual.py submissions roster.csv`

You should now see a folder called `codepost_upload`, whose subfolders correspond to students. Any problem files will show up in the `errors` folder.

> Optional flag '--simulate' will run the script without copying any files
> `python3 brightspace_to_codepost_manual.py submissions roster.csv --simulate`

## 4. Upload to codePost

Navigate to [codepost.io](https://codepost.io), log in, and click `Assignments -> Actions -> Upload Submissions -> Multiple Submissions`. Drag `codepost_upload` into codePost and voila.

If you prefer to have more control over the upload process, check out our [Python SDK](https://github.com/codepost-io/codepost-python).

## Special Case A: Partners

Many assignments will have students submit together in groups of 2 or more. Although Brightspace has the notion of "Groups", it doesn't have a way for students to independently decide to partner on an assignment and submit together.

If you want codePost to recognize group submissions, you can require your students to submit an extra file in their submission called `partners.txt` which contains the email address of each group member on a newline.

Like this:

```
partner1@school.edu
partner2@school.edu
partner3@school.edu
```

The `brightspace_to_codepost_manual` script will read this file from Brightspace and do the work necessary to make sure the students are recorded as partners on codePost.

# Exporting grades from codePost to Brightspace

Once all submissions for an assignment are graded on codePost, go to `codepost.io/admin -> Assignments -> Download Grades`.

Format the csv as necessary and upload to Brightspace by going to your Brightspace Instance -> Grade Book -> Import.
