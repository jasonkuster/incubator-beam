/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.beam.sdk.io.jdbc;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

import org.apache.beam.sdk.coders.BigEndianIntegerCoder;
import org.apache.beam.sdk.coders.KvCoder;
import org.apache.beam.sdk.coders.StringUtf8Coder;
import org.apache.beam.sdk.options.PipelineOptionsFactory;
import org.apache.beam.sdk.testing.PAssert;
import org.apache.beam.sdk.testing.TestPipeline;
import org.apache.beam.sdk.transforms.Count;
import org.apache.beam.sdk.transforms.Create;
import org.apache.beam.sdk.values.KV;
import org.apache.beam.sdk.values.PCollection;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;
import org.postgresql.ds.PGSimpleDataSource;


/**
 * A test of {@link org.apache.beam.sdk.io.jdbc.JdbcIO} on an independent Postgres instance.
 *
 * <p>This test requires a running instance of Postgres, and the test dataset must exist in the
 * database. `JdbcTestDataSet` will create the read table.
 *
 * <p>You can run just this test by doing the following:
 * <pre>
 * mvn test-compile compile failsafe:integration-test -D beamTestPipelineOptions='[
 * "--postgresServerName=1.2.3.4",
 * "--postgresUsername=postgres",
 * "--postgresDatabaseName=myfancydb",
 * "--postgresPassword=yourpassword",
 * "--postgresSsl=false"
 * ]' -DskipITs=false -Dit.test=org.apache.beam.sdk.io.jdbc.JdbcIOIT -DfailIfNoTests=false
 * </pre>
 */
@RunWith(JUnit4.class)
public class JdbcIOIT {
  private static PGSimpleDataSource dataSource;
  private static String writeTableName;

  @BeforeClass
  public static void setup() throws SQLException {
    PipelineOptionsFactory.register(PostgresTestOptions.class);
  }

  @AfterClass
  public static void tearDown() throws SQLException {
    JdbcTestDataSet.cleanUpDataTable(dataSource, writeTableName);
  }

  /**
   * Does a test read of a few rows from a postgres database.
   *
   * <p>Note that IT read tests must not do any data table manipulation (setup/clean up.)
   * @throws SQLException
   */
  @Test
  public void testRead() throws SQLException {
    PostgresTestOptions options = TestPipeline.testingPipelineOptions()
        .as(PostgresTestOptions.class);
    JdbcIOITReadPipeline.main(TestPipeline.convertToArgs(options));
  }

  
  /**
   * Tests writes to a postgres database.
   *
   * <p>Write Tests must clean up their data - in this case, it uses a new table every test run so
   * that it won't interfere with read tests/other write tests. It uses finally to attempt to
   * clean up data at the end of the test run.
   * @throws SQLException
   */
  /*
  @Test
  public void testWrite() throws SQLException {

    pipeline.run().waitUntilFinish();

    try (Connection connection = dataSource.getConnection()) {
      try (Statement statement = connection.createStatement()) {
        try (ResultSet resultSet = statement.executeQuery("select count(*) from "
            + writeTableName)) {
          resultSet.next();
          int count = resultSet.getInt(1);

          Assert.assertEquals(2000, count);
        }
      }
    }
    // TODO: Actually verify contents of the rows.
  }
  */
}
