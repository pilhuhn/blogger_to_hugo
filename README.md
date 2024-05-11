= Blogger 2 Hugo

Small script that goes through the export from blogger and creates a directory per article,
which contains the blog text rendered to Markdown as well as images attached to the original
post.

== Obtain the export

Go to [Blogger](https://www.blogger.com/) and then in the Settings scroll way down to 
"Save content". This will export a XML file, that is the input to
the script.

== Running

In the script at the top are 2 variables:

----
# File path for the exported file
in_file = "/tmp/blog-05-01-2024.xml"
# Where to write the output.
out_dir = "/tmp/blog"
----

Here the input XML file would be at _/tmp/blog-05-01-2024.xml_ and the
results of the script run would land in _/tmp/blog/_  with one sub-directory
per year.

After editing the above, just run the script

----
python3.12 blogger_to_hugo.py
----




