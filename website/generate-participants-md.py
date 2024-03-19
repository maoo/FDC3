from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
import json
import pprint
pp = pprint.PrettyPrinter(indent=4)

def get_google_client(var_map, scopes):
	credentials = ServiceAccountCredentials.from_json_keyfile_name(
    var_map['GOOGLE_AUTH_SECRET'], scopes)
	delegated_credentials = credentials.create_delegated(var_map['GOOGLE_AUTH_EMAIL'])
	h = Http()
	delegated_credentials.authorize(h)
	return h

def search_email(client,email_address):
	url = 'https://people.googleapis.com/v1/otherContacts:search?query={}&readMask=emailAddresses,names'.format(email_address)
	_, content = client.request(url, 'GET')
	json_content = json.loads(content)
	print(email_address)
	print(json_content)
	if 'results' in json_content:
		return json_content['results'][0]['person']['names'][0]['displayName']
	else:
		url = 'https://people.googleapis.com/v1/people:searchContacts?query={}&readMask=emailAddresses,names'.format(email_address)
		_, content = client.request(url, 'GET')
		json_content = json.loads(content)
		if 'results' in json_content:
			return json_content['results'][0]['person']['names'][0]['displayName']
		return None	

def get_ggroups_list_members(
		client,
		google_group):
	url = 'https://www.googleapis.com/admin/directory/v1/groups/{}/members'.format(google_group)
	_, content = client.request(url, 'GET')
	json_content = json.loads(content)
	contacts = {}
	if 'members' in json_content:
		members_json = json_content['members']
		# print(members_json)
		members_list = map(lambda x: x['email'], members_json)
		# print('Found {} Members in Google Group {} '.format(len(members_json),google_group))
		for member in members_list:
			member = member.lower()
			member_name = search_email(client,member)
			contacts[member] = {
				'email': member,
				'name': member_name
			}
	return contacts

var_map = {}
var_map['GOOGLE_AUTH_SECRET'] = '../service-account.json'
var_map['GOOGLE_AUTH_EMAIL'] = 'maoo@finos.org'
GOOGLE_AUTH_SCOPES = [
	'https://www.googleapis.com/auth/contacts.readonly',
	'https://www.googleapis.com/auth/contacts.other.readonly',
	'https://www.googleapis.com/auth/admin.directory.group.member',
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.orgunit',
    'https://www.googleapis.com/auth/admin.directory.domain'
]

client = get_google_client(var_map, GOOGLE_AUTH_SCOPES)

members = get_ggroups_list_members(client,"fdc3-participants@finos.org")

members_names = map(lambda x: [x, members[x]['name']], members)

names = []
for member in members_names:
	email = member[0]
	name = member[1]
	if name == None:
		name = "N/A {}".format(email) 
	names.append(name)

markdown = "# FDC3 Participants\n\n"
for name in set(names):
	markdown += "- {}\n".format(name)

print(markdown)