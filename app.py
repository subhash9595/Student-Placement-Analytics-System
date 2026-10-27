"""Student Placement Data Analysis System - Flask application factory."""
import os

import click
from flask import Flask, render_template

from config import Config
from extensions import db
from services.utils import pretty_skill


def create_app(overrides: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)
    db.init_app(app)

    from routes import analytics, dashboard, data_io, insights, placements, students
    for module in (dashboard, students, placements, analytics, insights, data_io):
        app.register_blueprint(module.bp)

    app.jinja_env.filters["skill"] = pretty_skill
    app.jinja_env.filters["lpa"] = lambda v: "-" if v is None or v != v else f"{v:.2f}"

    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", code=404, message="That page or record does not exist."), 404

    @app.errorhandler(413)
    def too_large(_):
        return render_template("error.html", code=413, message="The uploaded file is larger than 5 MB."), 413

    @app.errorhandler(500)
    def server_error(_):
        return render_template("error.html", code=500,
                               message="Something went wrong. Check the database connection and try again."), 500

    @app.cli.command("init-db")
    def init_db():
        """Create all database tables."""
        db.create_all()
        click.echo("Tables created.")

    @app.cli.command("seed")
    @click.option("--file", "path", default="sample_data/placement_sample.csv", show_default=True)
    def seed(path):
        """Load a CSV (default: the bundled sample data) into the database."""
        from services.importer import import_dataframe, read_csv
        with open(path, "rb") as fh:
            result = import_dataframe(read_csv(fh))
        click.echo(f"Imported {result['imported']} rows, skipped {result['skipped']}.")
        for e in result["errors"][:10]:
            click.echo(f"  row {e['row']}: {e['field']} {e['message']}")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "1") == "1")
