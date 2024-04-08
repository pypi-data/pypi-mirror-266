from invexpo.inverse_exponential import InverseExponential

# sample data that mimics an "exponentially increasing" function bounded by [600, 800]
data = [600, 625, 650, 675, 700, 710, 720, 730, 740, 750, 760, 770, 780, 790, 800]

invex = InverseExponential()
invex.fit(data)

print("Shape parameter:\t\t", invex.get_parameter())
print("Integral from [600, 700]:\t", invex.integrate(600, 700))
print("CDF of x = 750:\t\t\t", invex.cdf(750))
print("80th percentile:\t\t", invex.icdf(0.8)) # or invex.ppf(0.8), icdf is an alias
print("Mean:\t\t\t\t", invex.mean())
print("Median:\t\t\t\t", invex.median())
print("Variance:\t\t\t", invex.var())
print("Std. Dev:\t\t\t", invex.std())
print("2nd moment:\t\t\t", invex.moment(2))
print("5 new samples:\t\t\t", invex.rvs(5))
