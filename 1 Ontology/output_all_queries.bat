@echo off
set JENA_HOME=C:\Users\Mark.Jung\Documents\apache-jena-3.8.0

for %%F in (queries/*.rq) do (
    sparql --data=test1.owl --query=queries/%%F --results=csv > queries/%%~nF.csv
)
