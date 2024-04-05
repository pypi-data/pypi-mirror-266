# Statistical Analysis Toolkit

Welcome to `statanalysis`, a repository of statistical methods and tools tailored for data analysis enthusiasts. Inspired by my completion of a Coursera certificate in statistics, this repository encompasses a plethora of statistical concepts meticulously crafted into implementations. From prediction metrics to regression analysis, hypothesis testing to confidence intervals, and population parameter estimation to model estimation, `statanalysis` covers it all.

Built in Python, `statanalysis` provides meticulously crafted modules and utilities aimed at beginners in statistics, data science, and research. While following a certification on statistics on Coursera, I chose to solidify my knowledge through implementations instead of solely relying on existing modules. I believe there is no better way to understand a statistical formula than by implementing it in code, documenting it thoroughly, and validating the results through tests.

So, I've rewritten common statistical learning tools then create a repository that offers direct access to my implementations, ensuring simplicity without compromising accuracy. Futhermore, these implementations have undergone rigorous testing against established libraries like [scipy.stats](https://docs.scipy.org/doc/scipy/reference/stats.html), [statsmodels](https://www.statsmodels.org/stable/index.html), and [scikit-learn](https://scikit-learn.org/stable/modules/classes.html) to uphold industry standards.

Whether you're a novice or an experienced data analyst, `statanalysis` aims to simplify and enhance your statistical analysis journey. Dive in and explore a wealth of statistical methods and techniques designed to streamline your analytical processes and empower your insights.

## Features

1. **Utility Functions:**
   - **Module:** `utils_md`
   - **Description:** The `utils_md` module provides a collection of helper functions for various statistical tasks, including data preprocessing, standard deviation estimation, and computation of probabilities and percentiles.

1. **Hypothesis Validation:**
   - **Module:** `hyp_vali_md`
   - **Description:** The `hyp_vali_md` module includes functions for hypothesis validation, such as checking residuals, coefficients, and conducting hypothesis tests. Features encompass:
     - **Constraint Checking:** Functions for verifying constraints, such as checking if values fall within specific ranges.
     - **Hypothesis Sample Size:** Tools for ensuring minimum sample sizes for hypothesis testing scenarios.

1. **Confidence Interval Estimation:**
   - **Module:** `conf_inte_md`
   - **Description:** The `conf_inte_md` module offers methods for estimating confidence intervals for population parameters, such as proportions and means. Features include:
     - **One-sample Proportion:** Functions for estimating confidence intervals for population proportions based on a single sample.
     - **Two-sample Mean:** Methods for computing confidence intervals for the difference between two population means, considering paired and unpaired data.

1. **Hypothesis Testing:**
   - **Module:** `hyp_testi_md`
   - **Description:** This module encompasses a comprehensive suite of functions for hypothesis testing, covering a variety of scenarios:
     - **Testing Population Proportions:** Methods for assessing hypotheses related to population proportions using z-tests.
     - **Comparing Means:** Functions for conducting hypothesis tests to compare means between two or more populations, employing t-tests and ANOVA.

1. **Model Estimation:**
   - **Module:** `mdl_esti_md`
   - **Description:** The `mdl_esti_md` module houses classes and functions dedicated to model estimation. Notable features include:
     - **Linear Regression:** Implementation of linear regression models, including ordinary least squares (OLS) and robust regression.
     - **Logistic Regression:** Classes for logistic regression analysis, enabling binary classification tasks with probability predictions.
     - **Multiple Regression:** Tools for conducting multiple regression analysis, facilitating the exploration of relationships between multiple independent variables and a dependent variable.

## Repository Structure

The repository is organized into two main folders:

1. **`statanalysis/` Folder:**

   This folder contains the following modules:

   - **`utils_md:`** Module for utility functions, offering a collection of helper functions for statistical tasks.
   - **`hyp_vali_md:`** Module for hypothesis validation, containing functions for checking residuals, coefficients, and conducting hypothesis tests.
   - **`conf_inte_md:`** Module for confidence interval estimation, providing methods for estimating confidence intervals for proportions and means.
   - **`hyp_testi_md:`** Module for hypothesis testing, including functions for conducting hypothesis tests on proportions and means.
   - **`mdl_esti_md:`** Module for model estimation, including classes and functions for linear regression, logistic regression, and multiple regression.

2. **`tests/` Folder:**

   This folder features tests for all methods mentioned above.

## Usage

To utilize the statistical analysis functionalities provided by this library, you have either clone the repo or install from pypi depending on your usage

### **Clone the Repository:**

Clone the repository to your local machine using the following command:

```bash
git clone https://github.com/hermann-web/some-common-statistical-methods
```

### **Install the Library from PyPI:**

Install the library from PyPI using pip:

```bash
pip install statanalysis
```

Choose the option that best suits your needs and get started with your statistical analysis.

### **Import Modules or Functions:**

In your Python script, import the desired modules or functions using the following syntax:

```python
from statanalysis import utils_md, hyp_vali_md, conf_inte_md, hyp_testi_md, mdl_esti_md
```

### **Perform Statistical Analysis:**

Utilize the imported functions and classes to perform a wide range of statistical analysis tasks on your data. For example:

```python
# Example: Compute a confidence interval for a population proportion
confidence_interval = conf_inte_md.IC_PROPORTION_ONE(sample_size=100, parameter=0.5, confidence=0.95)
```

Leverage advanced statistical techniques and methodologies provided by the modules to analyze your data effectively.

Additionally, if you prefer to browse documentation in a more structured format, you can refer to the documentation files included in the repository, which provides detailed information about the library's functionalities and usage. There is a [detailled one](./docs/detailled-docu.md) and a[more concice one](./docs/concise-docu.md)

## Additional Information

- The repository includes a comprehensive test suite in [tests](./tests/) folder to validate the accuracy and consistency of the implemented methods against standard industry-standard libraries like scipy.stats, statsmodels, and scikit-learn.
- The module is available on PyPI for easy installation and use in various statistical analysis projects.
- For detailed explanations and references, refer to the respective sections in the code files.
- Further insights and explanations on statistical concepts can be found in the provided links.
- For inquiries or assistance regarding the repository, please contact [Hermann Agossou](mailto:hermannagossou7[at]gmail.com).
