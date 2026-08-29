"""Build the experimental Zinc physical-price regression on LME×USD intrinsic value."""

from __future__ import annotations

from pathlib import Path

import jdatetime
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler


def to_jalali(value: pd.Timestamp) -> str:
    return jdatetime.date.fromgregorian(date=value.date()).strftime("%Y/%m/%d")


def build(project: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    processed = project / "data" / "processed" / "bubble"
    processed.mkdir(parents=True, exist_ok=True)
    physical = pd.read_csv(processed / "physical_vs_intrinsic_bubble.csv")
    certificate = pd.read_csv(processed / "certificate_vs_intrinsic_bubble.csv")
    physical["date"] = pd.to_datetime(physical["date"])
    certificate["date"] = pd.to_datetime(certificate["date"])

    anchors = (
        certificate.loc[certificate["is_main_exact_anchor"].eq(1), ["date"]]
        .merge(physical[["date", "physical_price_irr_per_kg"]], on="date", how="inner", validate="one_to_one")
        .sort_values("date")
        .reset_index(drop=True)
    )
    if len(anchors) < 6:
        raise ValueError(f"At least six exact anchors are required; found {len(anchors)}")
    training = anchors.merge(
        certificate[["date", "intrinsic_price_irr_per_kg"]],
        on="date", how="left", validate="one_to_one",
    )
    feature = ["intrinsic_price_irr_per_kg"]
    target = "physical_price_irr_per_kg"
    x, y = training[feature], training[target]
    models = {
        "proportional_no_intercept": LinearRegression(fit_intercept=False),
        "linear_with_intercept": LinearRegression(),
        "polynomial_degree_2_ridge": Pipeline([
            ("poly", PolynomialFeatures(degree=2, include_bias=False)),
            ("scale", StandardScaler()),
            ("model", RidgeCV(alphas=np.logspace(-4, 4, 81))),
        ]),
    }
    rmse: dict[str, float] = {}
    splitter = TimeSeriesSplit(n_splits=5)
    for name, model in models.items():
        prediction = pd.Series(np.nan, index=y.index, dtype=float)
        for train_index, test_index in splitter.split(x):
            fitted = clone(model).fit(x.iloc[train_index], y.iloc[train_index])
            prediction.iloc[test_index] = fitted.predict(x.iloc[test_index])
        valid = prediction.notna()
        rmse[name] = mean_squared_error(y[valid], prediction[valid]) ** 0.5

    selected_name = min(rmse, key=rmse.get)
    selected_model = clone(models[selected_name]).fit(x, y)
    output = certificate[["date", "intrinsic_price_irr_per_kg", "certificate_price_irr_per_kg"]].copy()
    output = output.merge(anchors, on="date", how="left", validate="one_to_one")
    output["estimated_physical_price_irr_per_kg"] = selected_model.predict(output[feature])
    output["certificate_bubble_pct"] = (
        output["certificate_price_irr_per_kg"] / output["estimated_physical_price_irr_per_kg"] - 1
    ) * 100
    output.insert(1, "date_jalali", output["date"].map(to_jalali))
    output["is_actual_physical_observation"] = output[target].notna().astype(int)
    output["selected_model"] = selected_name
    output = output[[
        "date", "date_jalali", "intrinsic_price_irr_per_kg",
        "physical_price_irr_per_kg", "estimated_physical_price_irr_per_kg",
        "certificate_price_irr_per_kg", "certificate_bubble_pct",
        "is_actual_physical_observation", "selected_model",
    ]]
    metrics = pd.DataFrame(
        [{"model": name, "timeseries_cv_rmse": value, "selected": int(name == selected_name)} for name, value in rmse.items()]
    ).sort_values("timeseries_cv_rmse")
    output.to_csv(processed / "intrinsic_regression.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(processed / "intrinsic_regression_metrics.csv", index=False, encoding="utf-8-sig")
    return output, metrics


def main() -> None:
    output, metrics = build(Path(__file__).resolve().parents[3])
    selected = metrics.loc[metrics["selected"].eq(1), "model"].iloc[0]
    print(f"Selected model: {selected}")
    print(f"Rows: {len(output)}; anchors: {output['is_actual_physical_observation'].sum()}")


if __name__ == "__main__":
    main()
