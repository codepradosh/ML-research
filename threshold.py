above_threshold = composite_scores > threshold

plt.figure(figsize=(10, 6))
plt.plot(df['Time'], composite_scores, color='blue')
plt.scatter(df['Time'][1:][above_threshold], composite_scores[above_threshold], color='red', label='Above Threshold')
plt.scatter(df['Time'][1:][~above_threshold], composite_scores[~above_threshold], color='green', label='Below Threshold')
plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
plt.xlabel('Time')
plt.ylabel('Composite Score')
plt.title('Composite Function Graph')
plt.legend()
plt.show()
