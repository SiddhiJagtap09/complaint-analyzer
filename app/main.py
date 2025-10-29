from . import create_app  # factory
from typing import Optional

def main() -> None:
    app = create_app()
    app.run(host='0.0.0.0', port=8000)

if __name__ == '__main__':
    main()
