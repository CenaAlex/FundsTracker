from flask import Flask, render_template, request, redirect, flash
from dbhelper import (
    add_contribution,
    get_contributions_summary,
    get_friend_id_by_name,
    get_contributions_by_date,
    get_contributions_summary_grouped_by_date,
    get_db_connection,
)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    detailed_contributions, total_per_friend, overall_total = get_contributions_summary()
    contributions_by_date = get_contributions_summary_grouped_by_date()  # Ensure this is defined
    return render_template(
        'index.html', 
        detailed_contributions=detailed_contributions, 
        total_per_friend=total_per_friend, 
        overall_total=overall_total,
        contributions_by_date=contributions_by_date,  # Pass the grouped contributions to the template
        pagetitle="Fund Tracker"
    )

@app.route('/add', methods=['POST'])
def add_funds():
    friend_name = request.form['friend_name']
    amount = float(request.form['amount'])

    friend_id = get_friend_id_by_name(friend_name)
    if friend_id:
        add_contribution(friend_id, amount)
        flash("Contribution added successfully!", "success")
    else:
        flash("Friend not found!", "error")

    return redirect('/')

@app.route('/date/<date>')
def contributions_by_date(date):
    contributions = get_contributions_by_date(date)
    return render_template('date.html', contributions=contributions, pagetitle=f"Contributions on {date}")
 
@app.route('/reset', methods=['POST'])
def reset_contributions():
    conn = get_db_connection()
    with conn:
        # Delete all contributions
        conn.execute('DELETE FROM contributions')
    conn.close()
    flash("All contributions have been reset to zero.", "success")
    return redirect('/')
   
@app.route('/delete/<int:contribution_id>', methods=['POST'])
def delete_contribution(contribution_id):
    conn = get_db_connection()
    with conn:
        # Delete the specific contribution by its ID
        conn.execute('DELETE FROM contributions WHERE id = ?', (contribution_id,))
    conn.close()
    flash("Contribution deleted successfully.", "success")
    return redirect(request.referrer)  # Redirect back to the previous page


if __name__ == "__main__":
    app.run(debug=True)
