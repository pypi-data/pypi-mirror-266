import argparse

def main():
    parser = argparse.ArgumentParser(description="Add two numbers")
    parser.add_argument("number1", type=int, help="First number")
    parser.add_argument("number2", type=int, help="Second number")
    args = parser.parse_args()

    result = args.number1 + args.number2
    print(f"The result is {result}")

if __name__ == "__main__":
    main()