import os,sys

def is_api_request_STALLED(response):
	for string in [
		"I couldn't complete your request.",
		"Rephrase your prompt",
		"outside of my capabilities",
		"I'm unable to help",
		"I can't help you with that",
		"I'm unable to",
	]:
		if string in response or string.lower() in response.lower():
			return True

	return False