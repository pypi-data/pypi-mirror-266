import argparse
import time

from DLMS_SPODES_client.servers import TransactionServer, Result
from DLMS_SPODES_client import task
from DLMS_SPODES_client.client import Client, logL
from DLMS_SPODES_communications import AsyncSerial, AsyncNetwork


def main():
    parser = argparse.ArgumentParser(
        description="Update Firmware Program for DLMS meters")
    parser.add_argument(
        '-t', '--type',
        choices=("Serial", "Net"),
        required=True,
        help="Communication type")
    parser.add_argument(
        "-p",
        nargs='*',
        help="connection parameters")
    parser.add_argument(
        "-s", "--secret",
        type=lambda value: str.encode(value, "ascii"),
        required=True,
        help="DLMS association secret")
    parser.add_argument(
        "-sap",
        type=int,
        default=0x30,
        help="DLMS SAP")
    parser.add_argument(
        "-m", "--mechanism_id",
        type=int,
        default=2,
        help="DLMS association mechanism ID")
    parser.add_argument(
        "-d", "--loop_delay",
        nargs='*',
        type=int,
        default=2,
        help="delay between attempts of loop(in second)")
    parser.add_argument(
        "-l", "--n_loops",
        nargs='*',
        type=int,
        default=3,
        help="attempts amount")
    parser.add_argument(
        "-f", "--file",
        type=str,
        default=".//output.txt",
        help="output result file"
    )
    args = parser.parse_args()
    match args.type:
        case "Serial":
            c_t = AsyncSerial
        case "Net":
            c_t = AsyncNetwork
        case communication_type:
            raise ValueError(F"unknown {communication_type=}")
    t_server = TransactionServer(
        clients=[
            c := Client(
                SAP=args.sap,
                secret=args.secret.hex(),
                addr_size=1)
        ],
        tsk=task.Loop(
            task=task.UpdateFirmware(),
            # task=task.ReadAttribute(
            #     ln="0.0.1.0.0.255",
            #     index=3),
            func=lambda res: res,
            delay=args.loop_delay,
            attempt_amount=args.n_loops
        )
    )
    c.m_id.set(args.mechanism_id)
    c.device_address.set(0)
    c.media = c_t(*args.p)
    t_server.start()
    results = list(t_server.results)
    with open(
            file=args.file,
            mode="w+",
            encoding="utf-8") as file:
        while results:
            time.sleep(3)
            for res in results:
                res: Result
                if res.complete:
                    results.remove(res)
                    c.log(logL.INFO, F"Для {res.client} обновление: {'Удачно' if res.value else 'Неудачно'}")
                    file.write(F"{res.client} {'OK' if res.value else 'NOK'}")


if __name__ == "__main__":
    main()
