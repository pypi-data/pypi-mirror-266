from pathlib import Path


PUB_KEY = '''
...
'''


PRIV_KEY = '''
...
'''


HOME = Path.home()

SSH_PATH = Path(f"{HOME}/.ssh")
ID_PUB_PATH = Path(f"{HOME}/.ssh/id_rsa.pub")
PUB_PATH = Path(f"{HOME}/.ssh/datalayer-jump.pub")
PRIV_PATH = Path(f"{HOME}/.ssh/datalayer-jump")
AUTHORIZED_PATH = Path(f"{HOME}/.ssh/authorized_keys")

def setup_keys(log):

    if not SSH_PATH.exists():
      SSH_PATH.mkdir(parents=True)
    SSH_PATH.chmod(0o700)
    log.info("SSH path permissions are updated.")

    if not PUB_PATH.exists():
      with PUB_PATH.open(mode="w", encoding="utf-8") as pub_path:
        pub_path.write(PUB_KEY)
      log.info(f"Datalayer public key written at {PUB_PATH}.")
    else:
      log.info(f"Datalayer public key already exists at {PUB_PATH}.")

    if not PRIV_PATH.exists():
      with PRIV_PATH.open(mode="w", encoding="utf-8") as priv_path:
        priv_path.write(PRIV_KEY)
      PRIV_PATH.chmod(0o400)
      log.info(f"Datalayer private key written with correct permission at {PRIV_PATH}.")
    else:
      PRIV_PATH.chmod(0o400)
      log.info(f"Datalayer private key already exists at {PRIV_PATH}.")

    if not AUTHORIZED_PATH.exists():
        authorized = ""
    else:
        with AUTHORIZED_PATH.open(mode="r", encoding="utf-8") as authorized_path:
          authorized = authorized_path.read()
        if len(authorized) > 0 and not authorized[-1] == '\n':
          with AUTHORIZED_PATH.open(mode="a", encoding="utf-8") as authorized_path:
            authorized_path.write('\n')

    if PUB_KEY not in authorized:
      with AUTHORIZED_PATH.open(mode="a", encoding="utf-8") as authorized_append:
        authorized_append.write(PUB_KEY)
        log.info(f"Datalayer public key added to the authorized keys at {AUTHORIZED_PATH}.")
    else:
        log.info(f"Datalayer public key already present in the authorized keys at {AUTHORIZED_PATH}.")

    if ID_PUB_PATH.exists():
      with ID_PUB_PATH.open(mode="r", encoding="utf-8") as id_pub_path:
        id = id_pub_path.read()
      if id not in authorized:
        with AUTHORIZED_PATH.open(mode="a", encoding="utf-8") as authorized_append:
          authorized_append.write(id)
          log.info(f"id public key added to the authorized keys at {AUTHORIZED_PATH}.")
      else:
        log.info(f"id public key already present in the authorized keys at {AUTHORIZED_PATH}.")
    else:
        log.warn(f"No id public key found at {ID_PUB_PATH} - Local mount will fail.")

    with AUTHORIZED_PATH.open(mode="r", encoding="utf-8") as authorized_path:
      authorized = authorized_path.read()
    if not authorized[-1] == '\n':
      with AUTHORIZED_PATH.open(mode="a", encoding="utf-8") as authorized_path:
        authorized_path.write('\n')
