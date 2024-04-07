
.PHONY: git
git: ## Exec git command inside the project folder. You can specify any command to execute with the `c` flag. Ex. make git c=pull
	git -C $(PROJECT_FOLDER) $(c)

.PHONY: git.add
git.add: ## Exec git add -A command inside the project folder.
	git -C $(PROJECT_FOLDER) add -A

.PHONY: git.branch
git.branch: ## Exec git branch command inside the project folder.
	git -C $(PROJECT_FOLDER) branch

.PHONY: git.commit
git.commit: ## Exec git commit command inside the project folder.  You can specify the message with the `m` flag.
	git -C $(PROJECT_FOLDER) commit -m '$(m)'

.PHONY: git.fetch
git.fetch: ## Exec git fetch command inside the project folder.
	git -C $(PROJECT_FOLDER) fetch

.PHONY: git.pop
git.pop: ## Exec git stash pop command inside the project folder.
	git -C $(PROJECT_FOLDER) stash pop

.PHONY: git.pull
git.pull: ## Exec git pull command inside the project folder.
	git -C $(PROJECT_FOLDER) pull

.PHONY: git.push
git.push: ## Exec git push command inside the project folder.
	git -C $(PROJECT_FOLDER) push

.PHONY: git.stash
git.stash: ## Exec git stash command inside the project folder.
	git -C $(PROJECT_FOLDER) stash

.PHONY: git.status
git.status: ## Exec git status command inside the project folder.
	git -C $(PROJECT_FOLDER) status

.PHONY: git.submodules
git.submodules: ## Update the submodules.
	git -C $(PROJECT_FOLDER) submodule sync
	git -C $(PROJECT_FOLDER) submodule update --recursive --remote

.PHONY:
git.hooks.setup:
	@for file in $(BUILD_TOOLS_FOLDER)/$(TECHNOLOGY)/hooks/*; do \
        cp "$$file" "$(ROOT)/.git/hooks/$$(basename "$${file%.*}")"; \
        chmod +x "$(ROOT)/.git/hooks/$$(basename "$${file%.*}")"; \
    done