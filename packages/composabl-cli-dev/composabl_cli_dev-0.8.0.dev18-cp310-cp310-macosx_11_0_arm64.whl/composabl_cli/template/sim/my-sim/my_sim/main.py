# Copyright (C) Composabl, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import argparse
import asyncio
import os

import grpc
from composabl_core.networking.server import make
from server_impl import ServerImpl


async def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("HOST") or "[::]")
    parser.add_argument("--port", default=os.environ.get("PORT") or 1337, type=int)
    parser.add_argument("--env_init", default=os.environ.get("ENV_INIT") or "{}")
    parser.add_argument("--protocol", default=os.environ.get("PROTOCOL") or "grpc")

    args = parser.parse_args()

    try:
        args.env_init = eval(args.env_init)
    except Exception:
        args.env_init = {}

    print(f"Starting with arguments {args}")

    server = None

    try:
        server = make(ServerImpl, args.host, args.port, args.env_init, args.protocol)
        await server.start()
    except KeyboardInterrupt:
        print("KeyboardInterrupt, Gracefully stopping the server")
    except grpc.RpcError as e:
        print(f"gRPC error: {e}, Gracefully stopping the server")
    except Exception as e:
        print(f"Unknown error: {e}, Gracefully stopping the server")
    finally:
        if server is not None:
            await server.stop()


if __name__ == "__main__":
    asyncio.run(start())
