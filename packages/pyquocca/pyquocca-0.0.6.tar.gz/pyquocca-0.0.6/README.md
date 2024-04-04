# Challenge Standard Library.
To use this in a challenge, add the following to your challenge's Dockerfile (or similar in your requirements.txt!):
```Dockerfile
RUN pip install --extra-index-url https://6443:whatarejwts@pypi.hamishwhc.com/ pyquocca
```

If you use this in your requirements.txt file, please delete the file after running `pip install`, so that students aren't able to find the credentials in the container.