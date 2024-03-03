build:
	docker build . -t eremeev/links

push:
	docker push eremeev/links

test:
	py.test tests