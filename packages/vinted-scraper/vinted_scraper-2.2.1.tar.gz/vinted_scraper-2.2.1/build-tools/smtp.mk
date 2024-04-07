
.PHONY: smtp.smtp4dev
smtp.smtp4dev: ## Run smtp4dev docker image to expose the smpt server. The server will listen on the port 32001 and it will expose it's ui on url: http://localhost:3000/
	docker run --rm --name=smtp4dev-server -it -p 3000:80 -p 32001:25 rnwood/smtp4dev

