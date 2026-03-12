# Workflow

🏠 [Go back to README.md](/README.md)

![image](https://user-images.githubusercontent.com/8038046/220163720-79ad0848-e364-4bb7-9ab6-3991c78baf12.png)

## Trunk-Based Development Flow

We like it because is simple to maintain and very good for CI/CD.

- MAIN branch (aka MASTER): The source of truth, all deployments can only become from this branch.
- Features branches: To develop new features we will create a new branch (from MAIN). Is very important to keep as small as possible the features to develop, for bigger features should be split.
- Releases Branches (optional): Now we won't use them, ignore them.

Flow use case: Imagine that we must develop one new feature in the spring.

1. Create a branch to develop the new feature (if you want here, we can use the same name e.g.: Development, Features, ...).
2. Develop using frequent COMMITs and following the recommended conventions ([see how to do COMMITs](#how-to-do-commits))
3. Once the feature is developed, create PR ([see how to do PULL REQUEST](#how-to-do-pull-requests-pr))
4. Wait for another member of the team to approve the PR. After will be committed to the MAIN branch (create, rebase, or squash merge).
5. Remove the feature branch. We don't want to maintain branches. Because you can restore the branch if you want.
6. TAG last commit from MAIN before deploying (follow the semantic versioning, [see how to do TAG](#how-to-do-a-tags))
7. If some bug appears, we must FIX it directly on the MAIN branch. Go to step 6.

Flow use case: In the middle of new feature development appears a critical BUG that we must solve before.

1. Leave alive feature branch.
2. Fix the bug using the MAIN branch.
3. TAG last commit (follow the semantic versioning, see how to do TAG)
4. Deploy. While bugs exist, repeat from step 2.
5. Before returning to our feature branch, we must import the changes (this bugfix(es)) from the master.
   - **TIP**: Using this command (from our feature branch), we are putting in this order the last version (from master) and after appliyng our commits introduced in this branch.

        ```powershell
        git pull —rebase —autostash
        ```

   - Resolve possible conflicts (if exists).

## How to do COMMITs

Commit and push to the (feature) branch always as possible and never keep the changes in your local.
Every commit should let us build the project without errors.
Do small commits and frequently, avoid grouping all changes in only one commit.

### Recommended commit Conventions

Our Mission, find answers to our future questions 😂.

1. Separate the subject from the body with a blank line.
2. The subject should be no longer than 50 characters and the body 72.
3. Your commit message should not contain any whitespace errors.
4. Remove unnecessary punctuation marks.
5. Do not end the subject line with a period.
6. Capitalize the subject line and each paragraph.
7. Use the imperative mood in the subject line.
8. Use the body to explain **what** changes you have made and **why** you made them (because how is in the code).
9. Do not assume the reviewer understands what the original problem was, ensure you add it.
10. Do not think your code is self-explanatory.
11. Follow the commit convention defined by your team ([see next topic: semantic commit messages](#recommended-commit-conventions)).

### Semantic Commit Messages

See how a minor change to your commit message style can make you a better programmer.

```txt
Format: <type>(<scope>): <subject>

<scope> is optional

Example
feat: add hat wobble
^--^  ^------------^
|     |
|     +-> Summary in present tense.
|
+-------> Type: chore, docs, feat, fix, refactor, style, or test.
```

More Examples:

- ***feat**: (not required/optional: new feature for the user, not a new feature for build script).
- **fix**: (bug fix for the user, not a fix to a build script).
- **docs**: (changes to the documentation).
- **style**: (formatting, missing semicolons, etc.; no production code change).
- **refactor**: (refactoring production code, e.g., renaming a variable).
- **test**: (adding missing tests, refactoring tests; no production code change).
- **chore**: (updating grunt tasks etc.; no production code change).
- **BREAKING CHANGE**: introduces something that breaks the compatibility from the previous version AND implies changing the MAJOR version.

Example in to find all feats commits:

Helps to find commits in the future. If you follow this convention, then you can find something using filters by type.

More info:

- <https://www.conventionalcommits.org/en/v1.0.0-beta.2/>
- <https://www.freecodecamp.org/news/writing-good-commit-messages-a-practical-guide/>

### Why Use Conventional Commits

- Communicating the nature of changes to teammates, the public, and other stakeholders.
- Make it easier for people to contribute to your projects, by allowing them to explore a more structured commit history.
- Triggering build and publish processes.
- Automatically can be determinate a semantic version bump (based on the types of commits landed).
Automatically can be generated CHANGELOGs.

## How to do PULL REQUESTs (PR)

- Title should be no longer than 72 characters.
- If PR changes something from UI, include a screenshot with a description of changes (images can be dragged & drop directly to GitHub).
- Add a description with all the changes. It is hard you can add a UML (Unified Modeling Language) diagram to help as a description.

Using **squash and merge** we will see only one commit in the master after the PR instead to import all the history commits from the feature after the branch. Cleaning then all the unnecessary commits and helping to navigate better to the history commit on the main branch.

![image](https://user-images.githubusercontent.com/8038046/220163876-206e2699-bf6e-46cc-b788-03f659c3426a.png)

If you select **Rebase and merge**, the X commits did it in the branch will be rebased and added to the base branch.
This is how we will see the historical differences between both choices.

![image2](https://user-images.githubusercontent.com/8038046/220174469-384299f0-813a-4c3e-82bc-c0d9bafacc45.png)

## How to do a TAGs

Semantic versioning, for example, v1.2.5 means:

```txt
  v   1  . 2  . 5
^--^ ^--^ ^--^ ^--^
|     |    |     |
|     |    |     +-> Patch / Bugfix: When we fix bugs without add new
|     |    |         features or breaking changes, keep compatibility
|     |    |
|     |    +-> Minor version. New features that the changes don’t breaks
|     |        compatibility with the previous version
|     |
|     +-> Major version. Only if the version break the compatibility from
|         previous version
|
+-------> Starts always with V to indicate that is a version
```

### Command to create new TAG

From master/main branch:

```powershell
git tag -a v1.2.5 -m "here a title"
git push origin v1.2.5
```