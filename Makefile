test:
	@dcc exec api sh -c './manage.py test'
freeze:
	@scripts/freeze.sh