import pytest
from jinja2 import Environment, PackageLoader, select_autoescape


from solarforecastarbiter import datamodel


@pytest.fixture
def macro_test_template():
    def fn(macro_name_and_args):
        macro_template = f"{{% import 'macros.j2' as macros with context%}}{{{{macros.{macro_name_and_args} | safe }}}}"  # noqa
        env = Environment(
            loader=PackageLoader(
                'solarforecastarbiter.reports', 'templates/html'),
            autoescape=select_autoescape(['html', 'xml']),
            lstrip_blocks=True,
            trim_blocks=True
        )
        html_template = env.from_string(macro_template)
        return html_template
    return fn


metric_table_fx_vert_format = """<table class="table table-striped metric-table-fx-vert" style="width:100%;">
  <caption style="caption-side:top; text-align:center">
    Table of {} metrics
  </caption>
  <thead>
    <tr class="header">
      <th style="text-align: left;">Forecast</th>
        <th style="text-align: left;">MAE</th>
        <th style="text-align: left;">RMSE</th>
        <th style="text-align: left;">MBE</th>
        <th style="text-align: left;">Skill</th>
        <th style="text-align: left;">Cost</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>{}</td>
                <td>2</td>
                <td>2</td>
                <td>2</td>
                <td>2</td>
                <td>2</td>
      </tr>
  </tbody>
</table>
"""


def test_metric_table_fx_vert(report_with_raw, macro_test_template):
    metric_table_template = macro_test_template('metric_table_fx_vert(report_metrics,category,metric_ordering)')  # noqa
    metrics = report_with_raw.raw_report.metrics
    category = 'total'
    for i in range(3):
        expected_metric = (metrics[i],)
        rendered_metric_table = metric_table_template.render(
            report_metrics=expected_metric,
            category=category,
            metric_ordering=report_with_raw.report_parameters.metrics,
            human_metrics=datamodel.ALLOWED_METRICS)
        assert rendered_metric_table == metric_table_fx_vert_format.format(
            category, expected_metric[0].name)


metric_table_fx_horz_format = """<table class="table table-striped" style="width:100%;">
  <caption style="caption-side:top; text-align:center">
    Table of {0} metrics
  </caption>
  <thead>
    <tr class="header">
      <th></th>
        <th colspan="{1}" style="text-align: center;">{2}</th>
    </tr>
    <tr class="header">
      <th style="text-align: left;">{0} Value</th>
          <th style="test-align: center;">MAE</th>
          <th style="test-align: center;">RMSE</th>
          <th style="test-align: center;">MBE</th>
          <th style="test-align: center;">Skill</th>
          <th style="test-align: center;">Cost</th>
    </tr>
  </thead>
  <tbody>
      <tr>
        <td>1</td>
                  <td>2</td>
                  <td>2</td>
                  <td>2</td>
                  <td>2</td>
                  <td>2</td>
      </tr>
  </tbody>
</table>
"""


def test_metric_table_fx_horz(report_with_raw, macro_test_template):
    metric_table_template = macro_test_template('metric_table_fx_horz(report_metrics,category,metric_ordering)')  # noqa
    metrics = report_with_raw.raw_report.metrics
    category = 'hour'
    for i in range(3):
        expected_metric = (metrics[i],)
        rendered_metric_table = metric_table_template.render(
            report_metrics=expected_metric,
            category=category,
            metric_ordering=report_with_raw.report_parameters.metrics,
            human_metrics=datamodel.ALLOWED_METRICS)
        assert rendered_metric_table == metric_table_fx_horz_format.format(
            category, 5, expected_metric[0].name)


validation_table_format = """<table class="table table-striped validation-table" style="width:100%;">
  <caption style="caption-side:top; text-align:center">
    Table of data validation results
  </caption>
  <thead>
    <tr class="header">
      <th style="text-align: left;">Aligned Pair</th>
      <th style="text-align: center;">
        {}
      </th>
      <th style="text-align: center;">
        {}
      </th>
    </tr>
    <tr class="header">
      <th style="text-align: left;">Observation</th>
      <th style="text-align: center;">
        {}
      </th>
      <th style="text-align: center;">
        {}
      </th>
    </tr>
  </thead>
  <tbody>
      <tr>
      <td style="test-align: left">{}</td>
            <td style="text-align: center">0</td>
            <td style="text-align: center">0</td>
      </tr>
      <tr>
      <td style="test-align: left">{}</td>
            <td style="text-align: center">0</td>
            <td style="text-align: center">0</td>
      </tr>
      <tr>
      <td style="test-align: left">{}</td>
            <td style="text-align: center">0</td>
            <td style="text-align: center">0</td>
      </tr>
  </tbody>
</table>
"""


def test_validation_table(report_with_raw, macro_test_template):
    validation_table_template = macro_test_template('validation_table(proc_fxobs_list,quality_filters)')  # noqa
    proc_fxobs_list = report_with_raw.raw_report.processed_forecasts_observations[0:2]  # noqa
    qfilters = list(
        f.quality_flags for f in report_with_raw.report_parameters.filters
        if isinstance(f, datamodel.QualityFlagFilter))[0][0:3]
    rendered_validation_table = validation_table_template.render(
        proc_fxobs_list=proc_fxobs_list,
        quality_filters=qfilters)
    assert rendered_validation_table == validation_table_format.format(
        proc_fxobs_list[0].name,
        proc_fxobs_list[1].name,
        proc_fxobs_list[0].original.observation.name,
        proc_fxobs_list[1].original.observation.name,
        *qfilters)


preprocessing_table_format = """<table class="table table-striped preprocessing-table" style="width:100%;">
  <caption style="caption-side:top; text-align:center">
    Table of data preprocessing results
  </caption>
  <thead>
    <tr class="header">
      <th style="text-align: left;">Preprocessing Description</th>
      <th style="text-align: center;">
        {} <br>Number of Points
      </th>
      <th style="text-align: center;">
        {} <br>Number of Points
      </th>
    </tr>
  </thead>
  <tbody>
      <tr>
      <td style="test-align: left">{}</td>
            <td style="text-align: center">0</td>
            <td style="text-align: center">0</td>
      </tr>
      <tr>
      <td style="test-align: left">{}</td>
            <td style="text-align: center">0</td>
            <td style="text-align: center">0</td>
      </tr>
      <tr>
      <td style="test-align: left">{}</td>
            <td style="text-align: center">0</td>
            <td style="text-align: center">0</td>
      </tr>
      <tr>
      <td style="test-align: left">{}</td>
            <td style="text-align: center">0</td>
            <td style="text-align: center">0</td>
      </tr>
      <tr>
      <td style="test-align: left">{}</td>
            <td style="text-align: center">0</td>
            <td style="text-align: center">0</td>
      </tr>
  </tbody>
</table>
"""


def test_preprocessing_table(report_with_raw, macro_test_template,
                             preprocessing_result_types):
    preprocessing_table_template = macro_test_template('preprocessing_table(proc_fxobs_list)')  # noqa
    proc_fxobs_list = report_with_raw.raw_report.processed_forecasts_observations[0:2]  # noqa
    rendered_preprocessing_table = preprocessing_table_template.render(
        proc_fxobs_list=proc_fxobs_list)
    assert rendered_preprocessing_table == preprocessing_table_format.format(
        proc_fxobs_list[0].name,
        proc_fxobs_list[1].name,
        *preprocessing_result_types)
