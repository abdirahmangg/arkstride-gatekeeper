from pathlib import Path

comment = Path(
    "arkstride_pr_comment.md"
).read_text()

print("\nARKSTRIDE PR COMMENT\n")
print(comment)