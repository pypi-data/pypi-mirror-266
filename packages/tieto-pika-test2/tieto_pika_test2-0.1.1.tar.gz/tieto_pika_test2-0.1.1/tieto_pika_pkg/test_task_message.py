from tieto_pika.tieto_pika_pkg.agent_consume import receive_message


def handle_message():
    print("handle_new_message")


if __name__ == '__main__':
    receive_message(handle_message)
