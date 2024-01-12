"""
This module tests the correct installation of PuLP.  A correct installation will
end in a return code of 'OK'.

Author: Simon Griffiths
Date: 20-Nov-2023
Version: 1.0.0
"""
import pulp

def main() -> None:
    """
    Run the PuLP test
    """
    pulp.pulpTestAll()
    print("\nSolvers\n")
    print(pulp.listSolvers(onlyAvailable=True))
    
if __name__ == "__main__":
    main()