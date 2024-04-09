import streamit as st
from factorial_aivn.factorial import factorials

def main():
  st.title("Factorial Calculator")
  number = st.number_input("Entere a number:", min_value=0, max_value=900)
  if st.button("Calculate"):
    result = factorials(number)
    st.write(f"The factorial of {number} is {result}")
    st.balloons()
if __name__ == "__main__":
  main()
