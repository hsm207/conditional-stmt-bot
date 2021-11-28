jupyter:
	jupyter lab --allow-root & \
	sleep 5 && \
	jupyter server list

run-action-server:
	rasa run actions --auto-reload -vv

validate:
	rasa data validate

train: validate
	rasa train

run-bot: train
	rasa run \
		--enable-api \
		-vv \
		--cors "*"

shell: train
	rasa shell -vv