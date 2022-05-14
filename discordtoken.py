import sys

def get_discord_token():
    with open('DISCORD_TOKEN.txt', 'r', encoding = 'utf-8') as f:
        return f.readline()

def add_discord_token(token):
    with open('DISCORD_TOKEN.txt', 'w', encoding = 'utf-8') as f:
        f.write(token)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        add_discord_token(sys.argv[1])
    else:
        print("More than 1 argument was given. Please just give single argument")
